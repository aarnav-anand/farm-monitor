"""
Agronomic Analysis Service
Provides intelligent crop recommendations based on satellite and weather data
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


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
        area: float = 0
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
        
        # Calculate crop growth stage
        growth_stage = self._calculate_growth_stage(planting_date)
        
        # Assess crop health
        health_status = self._assess_crop_health(ndvi, crop_type, growth_stage)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            ndvi=ndvi,
            ndmi=ndmi,
            weather_analysis=weather_analysis,
            crop_type=crop_type,
            growth_stage=growth_stage,
            health_status=health_status
        )
        
        # Calculate risk assessment
        risks = self._assess_risks(weather_analysis, ndvi, ndmi)
        
        return {
            'health_status': health_status,
            'growth_stage': growth_stage,
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
        health_status: str
    ) -> str:
        """Generate actionable agronomic recommendations"""
        
        recommendations = []
        
        # NDVI-based recommendations
        if health_status in ["Poor", "Critical"]:
            recommendations.append(
                "⚠️ Low vegetation health detected. Inspect field for: "
                "(1) Nutrient deficiencies - consider soil testing, "
                "(2) Pest or disease pressure, "
                "(3) Water stress."
            )
        elif health_status == "Excellent":
            recommendations.append(
                "✅ Crops showing excellent health. Maintain current practices."
            )
        
        # Water stress recommendations
        if ndmi < 0.2:
            recommendations.append(
                "💧 Low moisture detected (NDMI < 0.2). Consider irrigation if water is available. "
                "Monitor crop water stress symptoms."
            )
        elif ndmi > 0.5:
            recommendations.append(
                "💧 High moisture levels detected. Ensure proper drainage to prevent waterlogging."
            )
        
        # Weather-based recommendations
        if weather_analysis.get('drought_risk'):
            recommendations.append(
                "🌵 Drought risk: Less than 20mm rainfall in past 30 days. "
                "Implement water conservation: mulching, reduce tillage, consider irrigation."
            )
        
        if weather_analysis.get('flood_risk'):
            recommendations.append(
                "🌊 Heavy rainfall expected (>100mm in next 7 days). "
                "Prepare drainage systems, avoid field operations until soil dries."
            )
        
        if weather_analysis.get('temperature_stress'):
            avg_temp = weather_analysis.get('avg_temperature', 25)
            if avg_temp > 35:
                recommendations.append(
                    "🌡️ High temperature stress (avg >35°C). "
                    "Ensure adequate irrigation, monitor for heat stress symptoms."
                )
            elif avg_temp < 10:
                recommendations.append(
                    "❄️ Low temperature detected (avg <10°C). "
                    "Monitor for frost damage, delay sensitive operations."
                )
        
        # Rainfall forecast
        forecast_rain = weather_analysis.get('forecast_rain_7d', 0)
        if forecast_rain == 0:
            recommendations.append(
                "☀️ No rainfall expected in next 7 days. Plan irrigation accordingly."
            )
        elif forecast_rain > 50:
            recommendations.append(
                "🌧️ Significant rainfall expected. Delay fertilizer/pesticide applications."
            )
        
        # Growth stage specific
        if growth_stage == "Flowering" and health_status in ["Good", "Excellent"]:
            recommendations.append(
                "🌸 Critical flowering stage detected. Ensure optimal water and nutrients. "
                "Avoid stress during this period for maximum yield."
            )
        
        # Fungal disease risk
        total_rain = weather_analysis.get('total_rainfall_30d', 0)
        avg_temp = weather_analysis.get('avg_temperature', 25)
        if total_rain > 80 and 20 < avg_temp < 30:
            recommendations.append(
                "🍄 Conditions favorable for fungal diseases (high rain + moderate temp). "
                "Scout regularly, consider preventive fungicide if disease pressure is high."
            )
        
        # Default recommendation if list is empty
        if not recommendations:
            recommendations.append(
                "✅ Crops appear healthy. Continue regular monitoring and maintain good agricultural practices."
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
