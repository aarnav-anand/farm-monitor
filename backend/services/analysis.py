"""
Agronomic Analysis Service
Provides intelligent crop recommendations based on satellite and weather data
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

from services.localization import (
    normalize_lang,
    translate_growth_stage,
    translate_health_status,
)

class AgronomicAnalyzer:
    """Analyzes farm data and provides agronomic recommendations"""
    
    # NDVI thresholds for different crops
    CROP_NDVI_THRESHOLDS = {
        'wheat': {'excellent': 0.7, 'good': 0.5, 'moderate': 0.3, 'poor': 0.2},
        'corn': {'excellent': 0.75, 'good': 0.55, 'moderate': 0.35, 'poor': 0.25},
        'rice': {'excellent': 0.8, 'good': 0.6, 'moderate': 0.4, 'poor': 0.3},
        'soybean': {'excellent': 0.7, 'good': 0.5, 'moderate': 0.3, 'poor': 0.2},
        'cotton': {'excellent': 0.65, 'good': 0.45, 'moderate': 0.3, 'poor': 0.2},
        'vegetables': {'excellent': 0.7, 'good': 0.5, 'moderate': 0.35, 'poor': 0.25},
        'fruit': {'excellent': 0.75, 'good': 0.55, 'moderate': 0.4, 'poor': 0.3},
        'other': {'excellent': 0.7, 'good': 0.5, 'moderate': 0.3, 'poor': 0.2}
    }
    
    def analyze(
        self,
        weather_data: Dict,
        satellite_data: Dict,
        crop_type: str,
        planting_date: Optional[str] = None,
        area: float = 0,
        language: Optional[str] = "en"
    ) -> Dict:
        """
        Perform comprehensive agronomic analysis
        
        Args:
            weather_data: Weather analysis from WeatherService
            satellite_data: Satellite data from SatelliteService
            crop_type: Type of crop being grown
            planting_date: Date when crop was planted
            area: Field area in hectares
            
        Returns:
            Dictionary with analysis results and recommendations
        """
        
        # Extract key metrics
        ndvi = satellite_data.get('ndvi_mean', 0.5)
        ndmi = satellite_data.get('ndmi_mean', 0.3)
        
        weather_analysis = weather_data.get('analysis', {})
        total_rain = weather_analysis.get('total_rainfall_30d', 0)
        forecast_rain = weather_analysis.get('forecast_rain_7d', 0)
        avg_temp = weather_analysis.get('avg_temperature', 25)
        
        lang = normalize_lang(language)

        # Calculate crop growth stage
        growth_stage_en = self._calculate_growth_stage(planting_date)
        growth_stage = translate_growth_stage(lang, growth_stage_en)
        
        # Assess crop health
        health_status_en = self._assess_crop_health(ndvi, crop_type, growth_stage_en)
        health_status = translate_health_status(lang, health_status_en)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            ndvi=ndvi,
            ndmi=ndmi,
            weather_analysis=weather_analysis,
            crop_type=crop_type,
            growth_stage=growth_stage_en,
            health_status=health_status_en,
            language=lang
        )
        
        # Calculate risk assessment
        risks = self._assess_risks(weather_analysis, ndvi, ndmi)
        
        return {
            'health_status': health_status,
            'health_status_en': health_status_en,
            'growth_stage': growth_stage,
            'growth_stage_en': growth_stage_en,
            'recommendations': recommendations,
            'risks': risks,
            'metrics': {
                'ndvi': ndvi,
                'ndmi': ndmi,
                'rainfall_30d': total_rain,
                'forecast_rain_7d': forecast_rain,
                'avg_temperature': avg_temp
            }
        }
    
    def _calculate_growth_stage(self, planting_date: Optional[str]) -> str:
        """Calculate crop growth stage based on planting date"""
        if not planting_date:
            return "Unknown"
        
        try:
            planted = datetime.strptime(planting_date, "%Y-%m-%d")
            days_since_planting = (datetime.now() - planted).days
            
            if days_since_planting < 0:
                return "Not Planted"
            elif days_since_planting < 30:
                return "Early Growth"
            elif days_since_planting < 60:
                return "Vegetative"
            elif days_since_planting < 90:
                return "Flowering"
            elif days_since_planting < 120:
                return "Fruiting/Grain Fill"
            else:
                return "Maturity/Harvest"
                
        except Exception as e:
            logger.error(f"Error calculating growth stage: {str(e)}")
            return "Unknown"
    
    def _assess_crop_health(self, ndvi: float, crop_type: str, growth_stage: str) -> str:
        """Assess overall crop health based on NDVI"""
        
        # Get crop-specific thresholds
        thresholds = self.CROP_NDVI_THRESHOLDS.get(
            crop_type.lower(),
            self.CROP_NDVI_THRESHOLDS['other']
        )
        
        if ndvi >= thresholds['excellent']:
            return "Excellent"
        elif ndvi >= thresholds['good']:
            return "Good"
        elif ndvi >= thresholds['moderate']:
            return "Moderate"
        elif ndvi >= thresholds['poor']:
            return "Poor"
        else:
            return "Critical"
    
    def _generate_recommendations(
        self,
        ndvi: float,
        ndmi: float,
        weather_analysis: Dict,
        crop_type: str,
        growth_stage: str,
        health_status: str,
        language: str = "en"
    ) -> str:
        """Generate actionable agronomic recommendations"""
        
        recommendations = []

        lang = normalize_lang(language)

        def tr(en: str, hi: str, gu: str) -> str:
            if lang == "hi":
                return hi
            if lang == "gu":
                return gu
            return en
        
        # NDVI-based recommendations
        if health_status in ["Poor", "Critical"]:
            recommendations.append(
                tr(
                    "Low vegetation health detected. Inspect field for: (1) Nutrient deficiencies (consider soil testing), (2) Pest/disease pressure, (3) Water stress.",
                    "वनस्पति स्वास्थ्य कम है। जाँच करें: (1) पोषक तत्व की कमी (मृदा परीक्षण पर विचार करें), (2) कीट/रोग दबाव, (3) पानी की कमी/तनाव।",
                    "વનસ્પતિ આરોગ્ય ઓછું છે. તપાસો: (1) પોષક તત્વોની કમી (માટી પરીક્ષણ વિચાર કરો), (2) કીટ/રોગ દબાણ, (3) પાણીની અછત/તાણ."
                )
            )
        elif health_status == "Excellent":
            recommendations.append(
                tr(
                    "Crops showing excellent health. Maintain current practices.",
                    "फसल का स्वास्थ्य उत्कृष्ट है। वर्तमान प्रथाएँ जारी रखें।",
                    "પાકનું આરોગ્ય ઉત્તમ છે. હાલની પદ્ધતિઓ ચાલુ રાખો."
                )
            )
        
        # Water stress recommendations
        if ndmi < 0.2:
            recommendations.append(
                tr(
                    "Low moisture detected (NDMI < 0.2). Consider irrigation if water is available. Monitor crop water-stress symptoms.",
                    "कम नमी मिली (NDMI < 0.2)। पानी उपलब्ध हो तो सिंचाई पर विचार करें। पानी-तनाव के लक्षणों की निगरानी करें।",
                    "ઓછી ભેજ મળી (NDMI < 0.2). પાણી ઉપલબ્ધ હોય તો સિંચાઈ વિચારો. પાણી-તાણના લક્ષણો પર નજર રાખો."
                )
            )
        elif ndmi > 0.5:
            recommendations.append(
                tr(
                    "High moisture levels detected. Ensure proper drainage to prevent waterlogging.",
                    "अधिक नमी मिली। जलभराव से बचने के लिए उचित जल निकासी सुनिश्चित करें।",
                    "વધારે ભેજ મળી. પાણી ભરાવ અટકાવવા યોગ્ય નિકાસ સુનિશ્ચિત કરો."
                )
            )
        
        # Weather-based recommendations
        if weather_analysis.get('drought_risk'):
            recommendations.append(
                tr(
                    "Drought risk: <20mm rainfall in past 30 days. Implement water conservation (mulching, reduced tillage) and consider irrigation.",
                    "सूखा जोखिम: पिछले 30 दिनों में <20mm वर्षा। जल संरक्षण (मल्चिंग, कम जुताई) अपनाएँ और सिंचाई पर विचार करें।",
                    "સૂકા જોખમ: છેલ્લા 30 દિવસમાં <20mm વરસાદ. પાણી બચત (મલ્ચિંગ, ઓછી ખેડ) અપનાવો અને સિંચાઈ વિચાર કરો."
                )
            )
        
        if weather_analysis.get('flood_risk'):
            recommendations.append(
                tr(
                    "Heavy rainfall expected (>100mm in next 7 days). Prepare drainage systems; avoid field operations until soil dries.",
                    "भारी वर्षा की संभावना (>100mm अगले 7 दिनों में)। जल निकासी तैयार रखें; मिट्टी सूखने तक खेत कार्य से बचें।",
                    "ભારે વરસાદની શક્યતા (>100mm આગામી 7 દિવસમાં). નિકાસ વ્યવસ્થા તૈયાર રાખો; માટી સૂકાય ત્યાં સુધી ખેતર કાર્ય ટાળો."
                )
            )
        
        if weather_analysis.get('temperature_stress'):
            avg_temp = weather_analysis.get('avg_temperature', 25)
            if avg_temp > 35:
                recommendations.append(
                    tr(
                        "High temperature stress (avg >35°C). Ensure adequate irrigation and monitor heat-stress symptoms.",
                        "उच्च तापमान तनाव (औसत >35°C)। पर्याप्त सिंचाई सुनिश्चित करें और गर्मी-तनाव के लक्षण देखें।",
                        "ઉંચા તાપમાનનું તાણ (સરેરાશ >35°C). પૂરતી સિંચાઈ સુનિશ્ચિત કરો અને ઉષ્ણતા-તાણના લક્ષણો તપાસો."
                    )
                )
            elif avg_temp < 10:
                recommendations.append(
                    tr(
                        "Low temperature detected (avg <10°C). Monitor frost damage and delay sensitive operations.",
                        "कम तापमान (औसत <10°C)। पाला क्षति पर नजर रखें और संवेदनशील कार्य टालें।",
                        "ઓછું તાપમાન (સરેરાશ <10°C). હિમ નુકસાન પર નજર રાખો અને સંવેદનશીલ કામગીરી ટાળો."
                    )
                )
        
        # Rainfall forecast
        forecast_rain = weather_analysis.get('forecast_rain_7d', 0)
        if forecast_rain == 0:
            recommendations.append(
                tr(
                    "No rainfall expected in next 7 days. Plan irrigation accordingly.",
                    "अगले 7 दिनों में वर्षा की संभावना नहीं। सिंचाई की योजना बनाएं।",
                    "આગામી 7 દિવસમાં વરસાદની શક્યતા નથી. તે મુજબ સિંચાઈ આયોજન કરો."
                )
            )
        elif forecast_rain > 50:
            recommendations.append(
                tr(
                    "Significant rainfall expected. Delay fertilizer/pesticide applications.",
                    "काफी वर्षा की संभावना। उर्वरक/कीटनाशक का प्रयोग टालें।",
                    "મોટા પ્રમાણમાં વરસાદની શક્યતા. ખાતર/કીટનાશકનું છંટકાવ મુલતવી રાખો."
                )
            )
        
        # Growth stage specific
        if growth_stage == "Flowering" and health_status in ["Good", "Excellent"]:
            recommendations.append(
                tr(
                    "Critical flowering stage detected. Ensure optimal water and nutrients; avoid stress during this period for maximum yield.",
                    "फूलने की महत्वपूर्ण अवस्था। पानी व पोषक तत्व सर्वोत्तम रखें; इस अवधि में तनाव से बचें।",
                    "ફૂલાવસ્થા મહત્વપૂર્ણ છે. પાણી અને પોષક તત્ત્વો યોગ્ય રાખો; આ સમયગાળા દરમિયાન તાણ ટાળો."
                )
            )
        
        # Fungal disease risk
        total_rain = weather_analysis.get('total_rainfall_30d', 0)
        avg_temp = weather_analysis.get('avg_temperature', 25)
        if total_rain > 80 and 20 < avg_temp < 30:
            recommendations.append(
                tr(
                    "Conditions favorable for fungal diseases (high rain + moderate temp). Scout regularly; consider preventive fungicide if disease pressure is high.",
                    "फफूंद रोग के लिए अनुकूल स्थितियाँ (अधिक वर्षा + मध्यम तापमान)। नियमित निगरानी करें; दबाव अधिक हो तो निवारक फफूंदनाशक पर विचार करें।",
                    "ફૂગજન્ય રોગ માટે અનુકૂળ પરિસ્થિતિ (વધારે વરસાદ + મધ્યમ તાપમાન). નિયમિત નિરીક્ષણ કરો; દબાણ વધારે હોય તો રોકથામ માટે ફૂગનાશક વિચાર કરો."
                )
            )
        
        # Default recommendation if list is empty
        if not recommendations:
            recommendations.append(
                tr(
                    "Crops appear healthy. Continue regular monitoring and maintain good agricultural practices.",
                    "फसल स्वस्थ दिखती है। नियमित निगरानी जारी रखें और अच्छी कृषि पद्धतियाँ अपनाएँ।",
                    "પાક સ્વસ્થ લાગે છે. નિયમિત નિરીક્ષણ ચાલુ રાખો અને સારી કૃષિ પદ્ધતિઓ જાળવો."
                )
            )
        
        return " | ".join(recommendations)
    
    def _assess_risks(self, weather_analysis: Dict, ndvi: float, ndmi: float) -> Dict:
        """Assess various agricultural risks"""
        
        risks = {
            'drought': 'Low',
            'flood': 'Low',
            'disease': 'Low',
            'heat_stress': 'Low',
            'overall': 'Low'
        }
        
        # Drought risk
        if weather_analysis.get('drought_risk') or ndmi < 0.2:
            risks['drought'] = 'High'
        elif weather_analysis.get('total_rainfall_30d', 50) < 30:
            risks['drought'] = 'Medium'
        
        # Flood risk
        if weather_analysis.get('flood_risk'):
            risks['flood'] = 'High'
        elif weather_analysis.get('forecast_rain_7d', 0) > 50:
            risks['flood'] = 'Medium'
        
        # Disease risk
        total_rain = weather_analysis.get('total_rainfall_30d', 0)
        avg_temp = weather_analysis.get('avg_temperature', 25)
        if total_rain > 80 and 20 < avg_temp < 30:
            risks['disease'] = 'High'
        elif total_rain > 50:
            risks['disease'] = 'Medium'
        
        # Heat stress risk
        if weather_analysis.get('temperature_stress'):
            risks['heat_stress'] = 'High'
        
        # Overall risk
        high_risks = sum(1 for r in risks.values() if r == 'High')
        medium_risks = sum(1 for r in risks.values() if r == 'Medium')
        
        if high_risks >= 2:
            risks['overall'] = 'High'
        elif high_risks >= 1 or medium_risks >= 2:
            risks['overall'] = 'Medium'
        
        return risks
