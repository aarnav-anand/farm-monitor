"""
PDF Report Generator
Creates professional farm monitoring reports
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from typing import Dict, Optional
import io
import base64
import logging
import os
from xml.sax.saxutils import escape as xml_escape

logger = logging.getLogger(__name__)

from services.localization import normalize_lang, t as tr


class PDFGenerator:
    """Generate PDF reports for farm monitoring"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._font_registered = False
        self._setup_custom_styles(language="en")
    
    def _register_fonts_if_available(self):
        if self._font_registered:
            return

        # Keep fonts inside repo so Render/local runs are consistent.
        base_dir = os.path.dirname(os.path.dirname(__file__))  # backend/
        fonts_dir = os.path.join(base_dir, "assets", "fonts")

        noto_sans = os.path.join(fonts_dir, "NotoSans-Regular.ttf")
        noto_deva = os.path.join(fonts_dir, "NotoSansDevanagari-Regular.ttf")
        noto_guj = os.path.join(fonts_dir, "NotoSansGujarati-Regular.ttf")

        try:
            if os.path.exists(noto_sans):
                pdfmetrics.registerFont(TTFont("NotoSans", noto_sans))
            if os.path.exists(noto_deva):
                pdfmetrics.registerFont(TTFont("NotoSansDevanagari", noto_deva))
            if os.path.exists(noto_guj):
                pdfmetrics.registerFont(TTFont("NotoSansGujarati", noto_guj))
            self._font_registered = True
        except Exception as e:
            logger.warning(f"Font registration failed, falling back to Helvetica: {e}")
            self._font_registered = True

    def _font_name_for_lang(self, language: str) -> str:
        lang = normalize_lang(language)
        if lang == "hi":
            return "NotoSansDevanagari"
        if lang == "gu":
            return "NotoSansGujarati"
        return "Helvetica"

    def _latin_font_name(self) -> str:
        # Prefer NotoSans if available; otherwise Helvetica is fine for ASCII.
        try:
            pdfmetrics.getFont("NotoSans")
            return "NotoSans"
        except Exception:
            return "Helvetica"

    def _mix_script_and_latin(self, text: str, lang: str) -> str:
        """
        ReportLab does not do font fallback. For hi/gu PDFs we want script glyphs AND
        English/digits/punctuation (ASCII). This returns a Paragraph-markup string that
        renders non-ASCII in the script font and ASCII runs in a Latin font.
        """
        if text is None:
            return ""
        s = str(text)
        if lang not in ("hi", "gu"):
            return xml_escape(s)

        script_font = self._font_name_for_lang(lang)
        latin_font = self._latin_font_name()

        out: list[str] = [f'<font face="{script_font}">']
        buf: list[str] = []
        in_ascii = None  # type: Optional[bool]

        def flush_ascii(ascii_mode: bool):
            nonlocal buf
            if not buf:
                return
            chunk = xml_escape("".join(buf))
            buf = []
            if ascii_mode:
                out.append(f'<font face="{latin_font}">{chunk}</font>')
            else:
                out.append(chunk)

        for ch in s:
            ascii_mode = ord(ch) < 128
            if in_ascii is None:
                in_ascii = ascii_mode
                buf.append(ch)
                continue
            if ascii_mode == in_ascii:
                buf.append(ch)
                continue
            flush_ascii(in_ascii)
            in_ascii = ascii_mode
            buf.append(ch)

        if in_ascii is not None:
            flush_ascii(in_ascii)

        out.append("</font>")
        return "".join(out)

    def _para(self, text: str, font_name: str, font_size: int = 10, color=colors.black, bold: bool = False) -> Paragraph:
        name = f"_tmp_{font_name}_{font_size}_{'b' if bold else 'r'}"
        style = ParagraphStyle(
            name=name,
            parent=self.styles["Normal"],
            fontName=font_name,
            fontSize=font_size,
            textColor=color,
            leading=font_size + 2,
        )
        return Paragraph(text, style)

    def _setup_custom_styles(self, language: str = "en"):
        """Setup custom paragraph styles"""
        self._register_fonts_if_available()

        font_regular = self._font_name_for_lang(language)
        font_bold = "Helvetica-Bold" if font_regular == "Helvetica" else font_regular
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2d6a4f'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=font_bold
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2d6a4f'),
            spaceAfter=12,
            spaceBefore=12,
            fontName=font_bold
        ))
        
        # Metric style
        self.styles.add(ParagraphStyle(
            name='Metric',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            fontName=font_regular
        ))
        
        # Recommendation style
        self.styles.add(ParagraphStyle(
            name='Recommendation',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=8,
            fontName=font_regular,
            textColor=colors.HexColor('#1b4332')
        ))
    
    def generate_report(
        self,
        farm_name: str,
        crop_type: str,
        area: float,
        center: Dict,
        weather_data: Dict,
        satellite_data: Dict,
        analysis: Dict,
        language: Optional[str] = "en"
    ) -> Dict:
        """
        Generate PDF report
        
        Returns:
            Dictionary with pdf_base64 and filename
        """
        
        try:
            lang = normalize_lang(language)
            # Recreate styles per language so correct font is used.
            self.styles = getSampleStyleSheet()
            self._setup_custom_styles(language=lang)

            # Create PDF in memory
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build content
            story = []
            
            # Header
            story.extend(self._create_header(farm_name, crop_type, area, center, lang))
            
            # Executive Summary
            story.extend(self._create_summary(analysis, satellite_data, lang))
            
            # Satellite Data Section
            story.extend(self._create_satellite_section(satellite_data, lang))
            
            # Weather Data Section
            story.extend(self._create_weather_section(weather_data, lang))
            
            # Recommendations Section
            story.extend(self._create_recommendations_section(analysis, lang))
            
            # Risk Assessment Section
            story.extend(self._create_risk_section(analysis, lang))
            
            # Footer
            story.extend(self._create_footer(lang))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            # Convert to base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            return {
                'pdf_base64': pdf_base64,
                'filename': f"{farm_name.replace(' ', '_')}_report_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
    
    def _create_header(self, farm_name: str, crop_type: str, area: float, center: Dict, lang: str) -> list:
        """Create report header"""
        story = []
        
        # Title
        title = Paragraph(tr(lang, "pdf_title"), self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Farm details table
        unit_hectares = "hectares"
        if lang == "hi":
            unit_hectares = "हेक्टेयर"
        elif lang == "gu":
            unit_hectares = "હેક્ટર"

        label_font = self._font_name_for_lang(lang)
        value_font = self._latin_font_name() if lang in ("hi", "gu") else self._font_name_for_lang(lang)

        def label_cell(k: str) -> Paragraph:
            return self._para(self._mix_script_and_latin(tr(lang, k), lang), label_font, font_size=11, color=colors.HexColor('#2d6a4f'), bold=True)

        def value_cell(v: str) -> Paragraph:
            # Values often contain ASCII (names, coordinates, month names). Render with latin-safe font.
            return self._para(xml_escape(str(v)), value_font, font_size=11, color=colors.black)

        data = [
            [label_cell("farm_name"), value_cell(farm_name)],
            [label_cell("crop_type"), value_cell(crop_type.title())],
            [label_cell("field_area"), value_cell(f"{area} {unit_hectares}")],
            [label_cell("location"), value_cell(f"{center['lat']:.4f}°N, {center['lng']:.4f}°E")],
            [label_cell("report_date"), value_cell(datetime.now().strftime('%B %d, %Y'))],
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _create_summary(self, analysis: Dict, satellite_data: Dict, lang: str) -> list:
        """Create executive summary"""
        story = []
        
        story.append(Paragraph(tr(lang, "executive_summary"), self.styles['SectionHeader']))
        
        health_status = analysis.get('health_status', 'Good')
        health_status_en = analysis.get('health_status_en', health_status)
        growth_stage = analysis.get('growth_stage', 'Unknown')
        ndvi = satellite_data.get('ndvi_mean', 0)
        
        # Health status with color coding
        color_map = {
            'Excellent': '#2d6a4f',
            'Good': '#40916c',
            'Moderate': '#f4a261',
            'Poor': '#e76f51',
            'Critical': '#c1121f'
        }
        
        health_color = color_map.get(health_status_en, '#6c757d')
        
        summary_text = f"""
        <b>{tr(lang, "crop_health_status")}</b> <font color="{health_color}"><b>{health_status}</b></font><br/>
        <b>{tr(lang, "growth_stage")}</b> {growth_stage}<br/>
        <b>{tr(lang, "vegetation_index")}</b> {ndvi:.3f}<br/>
        """
        
        story.append(Paragraph(summary_text, self.styles['Metric']))
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_satellite_section(self, satellite_data: Dict, lang: str) -> list:
        """Create satellite data section"""
        story = []
        
        story.append(Paragraph(tr(lang, "satellite_analysis"), self.styles['SectionHeader']))
        
        ndvi_mean = satellite_data.get('ndvi_mean', 0)
        ndvi_min = satellite_data.get('ndvi_min', 0)
        ndvi_max = satellite_data.get('ndvi_max', 0)
        ndmi_mean = satellite_data.get('ndmi_mean', 0)
        
        metadata = satellite_data.get('metadata', {})
        cloud_cover = metadata.get('cloud_cover', 'N/A')
        
        def pick(en: str, hi: str, gu: str) -> str:
            if lang == "hi":
                return hi
            if lang == "gu":
                return gu
            return en

        script_font = self._font_name_for_lang(lang)
        latin_font = self._latin_font_name()

        def hcell(txt: str) -> Paragraph:
            return self._para(self._mix_script_and_latin(txt, lang), script_font, font_size=11, color=colors.whitesmoke, bold=True)

        def scell(txt: str) -> Paragraph:
            return self._para(self._mix_script_and_latin(txt, lang), script_font, font_size=10, color=colors.black)

        def vcell(txt: str) -> Paragraph:
            return self._para(xml_escape(str(txt)), latin_font, font_size=10, color=colors.black)

        data = [
            [hcell(tr(lang, "metric")), hcell(tr(lang, "value")), hcell(tr(lang, "interpretation"))],
            [scell(pick("NDVI (Mean)", "NDVI (औसत)", "NDVI (સરેરાશ)")), vcell(f"{ndvi_mean:.3f}"), scell(self._interpret_ndvi(ndvi_mean, lang))],
            [scell(pick("NDVI Range", "NDVI सीमा", "NDVI શ્રેણી")), vcell(f"{ndvi_min:.3f} - {ndvi_max:.3f}"), scell(tr(lang, "field_variability"))],
            [scell(pick("NDMI (Moisture)", "NDMI (नमी)", "NDMI (ભેજ)")), vcell(f"{ndmi_mean:.3f}"), scell(self._interpret_ndmi(ndmi_mean, lang))],
            [scell(pick("Cloud Cover", "बादल आवरण", "વાદળ આવરણ")), vcell(f"{cloud_cover:.1f}%" if isinstance(cloud_cover, (int, float)) else str(cloud_cover)), scell(tr(lang, "image_quality"))],
        ]
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d6a4f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_weather_section(self, weather_data: Dict, lang: str) -> list:
        """Create weather analysis section"""
        story = []
        
        story.append(Paragraph(tr(lang, "weather_analysis"), self.styles['SectionHeader']))
        
        analysis = weather_data.get('analysis', {})
        
        total_rain = analysis.get('total_rainfall_30d', 0)
        forecast_rain = analysis.get('forecast_rain_7d', 0)
        avg_temp = analysis.get('avg_temperature', 0)
        rainfall_trend = analysis.get('rainfall_trend', 'stable')
        
        def pick(en: str, hi: str, gu: str) -> str:
            if lang == "hi":
                return hi
            if lang == "gu":
                return gu
            return en

        script_font = self._font_name_for_lang(lang)
        latin_font = self._latin_font_name()

        def hcell(txt: str) -> Paragraph:
            return self._para(self._mix_script_and_latin(txt, lang), script_font, font_size=11, color=colors.whitesmoke, bold=True)

        def scell(txt: str) -> Paragraph:
            return self._para(self._mix_script_and_latin(txt, lang), script_font, font_size=10, color=colors.black)

        def vcell(txt: str) -> Paragraph:
            return self._para(xml_escape(str(txt)), latin_font, font_size=10, color=colors.black)

        data = [
            [hcell(tr(lang, "metric")), hcell(tr(lang, "value")), hcell(tr(lang, "status"))],
            [scell(pick("Rainfall (30 days)", "वर्षा (30 दिन)", "વરસાદ (30 દિવસ)")), vcell(f"{total_rain:.1f} mm"), scell(self._interpret_rainfall(total_rain, lang))],
            [scell(pick("Forecast (7 days)", "पूर्वानुमान (7 दिन)", "પૂર્વાનુમાન (7 દિવસ)")), vcell(f"{forecast_rain:.1f} mm"), scell(tr(lang, "expected_precip"))],
            [scell(pick("Avg Temperature", "औसत तापमान", "સરેરાશ તાપમાન")), vcell(f"{avg_temp:.1f} °C"), scell(self._interpret_temperature(avg_temp, lang))],
            [scell(pick("Rainfall Trend", "वर्षा प्रवृत्ति", "વરસાદ વલણ")), vcell(rainfall_trend.title()), scell(tr(lang, "compared_prev_period"))],
        ]
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d6a4f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_recommendations_section(self, analysis: Dict, lang: str) -> list:
        """Create recommendations section"""
        story = []
        
        story.append(Paragraph(tr(lang, "agronomic_recommendations"), self.styles['SectionHeader']))
        
        recommendations = analysis.get('recommendations', '')
        
        # Split recommendations by separator
        rec_list = recommendations.split(' | ')
        
        for i, rec in enumerate(rec_list, 1):
            rec_text = f"{i}. {rec.strip()}"
            story.append(Paragraph(rec_text, self.styles['Recommendation']))
        
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_risk_section(self, analysis: Dict, lang: str) -> list:
        """Create risk assessment section"""
        story = []
        
        story.append(Paragraph(tr(lang, "risk_assessment"), self.styles['SectionHeader']))
        
        risks = analysis.get('risks', {})
        
        risk_colors = {
            'Low': colors.HexColor('#2d6a4f'),
            'Medium': colors.HexColor('#f4a261'),
            'High': colors.HexColor('#e76f51')
        }
        
        script_font = self._font_name_for_lang(lang)
        latin_font = self._latin_font_name()

        def hcell(txt: str) -> Paragraph:
            return self._para(self._mix_script_and_latin(txt, lang), script_font, font_size=11, color=colors.whitesmoke, bold=True)

        def scell(txt: str) -> Paragraph:
            return self._para(self._mix_script_and_latin(txt, lang), script_font, font_size=10, color=colors.black)

        def vcell(txt: str) -> Paragraph:
            return self._para(xml_escape(str(txt)), latin_font, font_size=10, color=colors.black)

        data = [
            [hcell(tr(lang, "risk_category")), hcell(tr(lang, "level"))],
            [scell(tr(lang, "drought_risk")), vcell(risks.get('drought', 'Low'))],
            [scell(tr(lang, "flood_risk")), vcell(risks.get('flood', 'Low'))],
            [scell(tr(lang, "disease_risk")), vcell(risks.get('disease', 'Low'))],
            [scell(tr(lang, "heat_stress_risk")), vcell(risks.get('heat_stress', 'Low'))],
            [scell(tr(lang, "overall_risk")), vcell(risks.get('overall', 'Low'))],
        ]
        
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d6a4f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _create_footer(self, lang: str) -> list:
        """Create report footer"""
        story = []
        
        footer_text = """
        <para alignment="center">
        <font size="8" color="#6c757d">
        {generated_by}<br/>
        {data_sources}<br/>
        Report generated on {}<br/>
        <i>{disclaimer}</i>
        </font>
        </para>
        """.format(
            datetime.now().strftime('%B %d, %Y at %I:%M %p'),
            generated_by=tr(lang, "generated_by"),
            data_sources=tr(lang, "data_sources"),
            disclaimer=tr(lang, "automated_disclaimer"),
        )
        
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        return story
    
    # Helper methods for interpretations
    
    def _interpret_ndvi(self, ndvi: float, lang: str = "en") -> str:
        """Interpret NDVI value"""
        def pick(en: str, hi: str, gu: str) -> str:
            if lang == "hi":
                return hi
            if lang == "gu":
                return gu
            return en

        if ndvi > 0.6:
            return pick("Excellent vegetation", "बहुत अच्छी वनस्पति", "ખૂબ સારી વનસ્પતિ")
        elif ndvi > 0.4:
            return pick("Good vegetation", "अच्छी वनस्पति", "સારી વનસ્પતિ")
        elif ndvi > 0.3:
            return pick("Moderate vegetation", "मध्यम वनस्पति", "મધ્યમ વનસ્પતિ")
        else:
            return pick("Low vegetation", "कम वनस्पति", "ઓછી વનસ્પતિ")
    
    def _interpret_ndmi(self, ndmi: float, lang: str = "en") -> str:
        """Interpret NDMI value"""
        def pick(en: str, hi: str, gu: str) -> str:
            if lang == "hi":
                return hi
            if lang == "gu":
                return gu
            return en

        if ndmi > 0.4:
            return pick("High moisture", "अधिक नमी", "વધારે ભેજ")
        elif ndmi > 0.2:
            return pick("Adequate moisture", "पर्याप्त नमी", "પૂરતું ભેજ")
        else:
            return pick("Low moisture / stress", "कम नमी / तनाव", "ઓછું ભેજ / તાણ")
    
    def _interpret_rainfall(self, rainfall: float, lang: str = "en") -> str:
        """Interpret rainfall amount"""
        def pick(en: str, hi: str, gu: str) -> str:
            if lang == "hi":
                return hi
            if lang == "gu":
                return gu
            return en

        if rainfall < 20:
            return pick("Very low - drought risk", "बहुत कम - सूखा जोखिम", "ખૂબ ઓછું - સૂકા જોખમ")
        elif rainfall < 50:
            return pick("Low - monitor closely", "कम - निगरानी करें", "ઓછું - નજીકથી નજર રાખો")
        elif rainfall < 100:
            return pick("Adequate", "पर्याप्त", "પૂરતું")
        elif rainfall < 150:
            return pick("Good", "अच्छा", "સારું")
        else:
            return pick("High - flood risk possible", "अधिक - बाढ़ जोखिम संभव", "વધારે - પૂર જોખમ શક્ય")
    
    def _interpret_temperature(self, temp: float, lang: str = "en") -> str:
        """Interpret temperature"""
        def pick(en: str, hi: str, gu: str) -> str:
            if lang == "hi":
                return hi
            if lang == "gu":
                return gu
            return en

        if temp < 10:
            return pick("Cold - potential stress", "ठंडा - तनाव संभव", "ઠંડું - તાણ શક્ય")
        elif temp < 20:
            return pick("Cool - good for growth", "ठंडा - वृद्धि के लिए अच्छा", "ઠંડક - વૃદ્ધિ માટે સારું")
        elif temp < 30:
            return pick("Optimal range", "उत्तम सीमा", "ઉત્તમ શ્રેણી")
        elif temp < 35:
            return pick("Warm - monitor water", "गर्म - पानी पर नजर रखें", "ગરમ - પાણી પર નજર રાખો")
        else:
            return pick("Hot - heat stress risk", "बहुत गर्म - गर्मी तनाव जोखिम", "ખૂબ ગરમ - ઉષ્ણતા તાણ જોખમ")
