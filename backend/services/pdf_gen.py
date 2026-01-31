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
from datetime import datetime
from typing import Dict
import io
import base64
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generate PDF reports for farm monitoring"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2d6a4f'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2d6a4f'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Metric style
        self.styles.add(ParagraphStyle(
            name='Metric',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        # Recommendation style
        self.styles.add(ParagraphStyle(
            name='Recommendation',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=8,
            fontName='Helvetica',
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
        analysis: Dict
    ) -> Dict:
        """
        Generate PDF report
        
        Returns:
            Dictionary with pdf_base64 and filename
        """
        
        try:
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
            story.extend(self._create_header(farm_name, crop_type, area, center))
            
            # Executive Summary
            story.extend(self._create_summary(analysis, satellite_data))
            
            # Satellite Data Section
            story.extend(self._create_satellite_section(satellite_data))
            
            # Weather Data Section
            story.extend(self._create_weather_section(weather_data))
            
            # Recommendations Section
            story.extend(self._create_recommendations_section(analysis))
            
            # Risk Assessment Section
            story.extend(self._create_risk_section(analysis))
            
            # Footer
            story.extend(self._create_footer())
            
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
    
    def _create_header(self, farm_name: str, crop_type: str, area: float, center: Dict) -> list:
        """Create report header"""
        story = []
        
        # Title
        title = Paragraph(f"🌾 Farm Monitoring Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Farm details table
        data = [
            ['Farm Name:', farm_name],
            ['Crop Type:', crop_type.title()],
            ['Field Area:', f"{area} hectares"],
            ['Location:', f"{center['lat']:.4f}°N, {center['lng']:.4f}°E"],
            ['Report Date:', datetime.now().strftime('%B %d, %Y')]
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2d6a4f')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _create_summary(self, analysis: Dict, satellite_data: Dict) -> list:
        """Create executive summary"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        health_status = analysis.get('health_status', 'Good')
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
        
        health_color = color_map.get(health_status, '#6c757d')
        
        summary_text = f"""
        <b>Crop Health Status:</b> <font color="{health_color}"><b>{health_status}</b></font><br/>
        <b>Growth Stage:</b> {growth_stage}<br/>
        <b>Vegetation Index (NDVI):</b> {ndvi:.3f}<br/>
        """
        
        story.append(Paragraph(summary_text, self.styles['Metric']))
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_satellite_section(self, satellite_data: Dict) -> list:
        """Create satellite data section"""
        story = []
        
        story.append(Paragraph("🛰️ Satellite Analysis", self.styles['SectionHeader']))
        
        ndvi_mean = satellite_data.get('ndvi_mean', 0)
        ndvi_min = satellite_data.get('ndvi_min', 0)
        ndvi_max = satellite_data.get('ndvi_max', 0)
        ndmi_mean = satellite_data.get('ndmi_mean', 0)
        
        metadata = satellite_data.get('metadata', {})
        cloud_cover = metadata.get('cloud_cover', 'N/A')
        
        data = [
            ['Metric', 'Value', 'Interpretation'],
            ['NDVI (Mean)', f"{ndvi_mean:.3f}", self._interpret_ndvi(ndvi_mean)],
            ['NDVI Range', f"{ndvi_min:.3f} - {ndvi_max:.3f}", 'Field variability'],
            ['NDMI (Moisture)', f"{ndmi_mean:.3f}", self._interpret_ndmi(ndmi_mean)],
            ['Cloud Cover', f"{cloud_cover:.1f}%" if isinstance(cloud_cover, (int, float)) else cloud_cover, 'Image quality'],
        ]
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d6a4f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_weather_section(self, weather_data: Dict) -> list:
        """Create weather analysis section"""
        story = []
        
        story.append(Paragraph("🌦️ Weather Analysis", self.styles['SectionHeader']))
        
        analysis = weather_data.get('analysis', {})
        
        total_rain = analysis.get('total_rainfall_30d', 0)
        forecast_rain = analysis.get('forecast_rain_7d', 0)
        avg_temp = analysis.get('avg_temperature', 0)
        rainfall_trend = analysis.get('rainfall_trend', 'stable')
        
        data = [
            ['Metric', 'Value', 'Status'],
            ['Rainfall (30 days)', f"{total_rain:.1f} mm", self._interpret_rainfall(total_rain)],
            ['Forecast (7 days)', f"{forecast_rain:.1f} mm", 'Expected precipitation'],
            ['Avg Temperature', f"{avg_temp:.1f} °C", self._interpret_temperature(avg_temp)],
            ['Rainfall Trend', rainfall_trend.title(), 'Compared to previous period'],
        ]
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d6a4f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_recommendations_section(self, analysis: Dict) -> list:
        """Create recommendations section"""
        story = []
        
        story.append(Paragraph("🌾 Agronomic Recommendations", self.styles['SectionHeader']))
        
        recommendations = analysis.get('recommendations', '')
        
        # Split recommendations by separator
        rec_list = recommendations.split(' | ')
        
        for i, rec in enumerate(rec_list, 1):
            rec_text = f"{i}. {rec.strip()}"
            story.append(Paragraph(rec_text, self.styles['Recommendation']))
        
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_risk_section(self, analysis: Dict) -> list:
        """Create risk assessment section"""
        story = []
        
        story.append(Paragraph("⚠️ Risk Assessment", self.styles['SectionHeader']))
        
        risks = analysis.get('risks', {})
        
        risk_colors = {
            'Low': colors.HexColor('#2d6a4f'),
            'Medium': colors.HexColor('#f4a261'),
            'High': colors.HexColor('#e76f51')
        }
        
        data = [
            ['Risk Category', 'Level'],
            ['Drought Risk', risks.get('drought', 'Low')],
            ['Flood Risk', risks.get('flood', 'Low')],
            ['Disease Risk', risks.get('disease', 'Low')],
            ['Heat Stress Risk', risks.get('heat_stress', 'Low')],
            ['Overall Risk', risks.get('overall', 'Low')],
        ]
        
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d6a4f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _create_footer(self) -> list:
        """Create report footer"""
        story = []
        
        footer_text = """
        <para alignment="center">
        <font size="8" color="#6c757d">
        This report was generated by Farm Monitor - A Zero-Cost Farm Monitoring System<br/>
        Data Sources: Sentinel-2 (ESA) • Open-Meteo • OpenStreetMap<br/>
        Report generated on {}<br/>
        <i>This is an automated analysis. Always verify recommendations with local agronomists.</i>
        </font>
        </para>
        """.format(datetime.now().strftime('%B %d, %Y at %I:%M %p'))
        
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        return story
    
    # Helper methods for interpretations
    
    def _interpret_ndvi(self, ndvi: float) -> str:
        """Interpret NDVI value"""
        if ndvi > 0.6:
            return "Excellent vegetation"
        elif ndvi > 0.4:
            return "Good vegetation"
        elif ndvi > 0.3:
            return "Moderate vegetation"
        else:
            return "Low vegetation"
    
    def _interpret_ndmi(self, ndmi: float) -> str:
        """Interpret NDMI value"""
        if ndmi > 0.4:
            return "High moisture"
        elif ndmi > 0.2:
            return "Adequate moisture"
        else:
            return "Low moisture / stress"
    
    def _interpret_rainfall(self, rainfall: float) -> str:
        """Interpret rainfall amount"""
        if rainfall < 20:
            return "Very low - drought risk"
        elif rainfall < 50:
            return "Low - monitor closely"
        elif rainfall < 100:
            return "Adequate"
        elif rainfall < 150:
            return "Good"
        else:
            return "High - flood risk possible"
    
    def _interpret_temperature(self, temp: float) -> str:
        """Interpret temperature"""
        if temp < 10:
            return "Cold - potential stress"
        elif temp < 20:
            return "Cool - good for growth"
        elif temp < 30:
            return "Optimal range"
        elif temp < 35:
            return "Warm - monitor water"
        else:
            return "Hot - heat stress risk"
