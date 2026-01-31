"""
Weather Service - Open-Meteo Integration
Fetches historical and forecast weather data
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class WeatherService:
    """Service to fetch weather data from Open-Meteo API"""
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1"
        self.archive_url = f"{self.base_url}/archive"
        self.forecast_url = f"{self.base_url}/forecast"
    
    async def get_weather_analysis(
        self,
        latitude: float,
        longitude: float,
        days_history: int = 30
    ) -> Dict:
        """
        Get comprehensive weather analysis including historical and forecast data
        
        Args:
            latitude: Farm center latitude
            longitude: Farm center longitude
            days_history: Number of historical days to fetch
            
        Returns:
            Dictionary with weather analysis
        """
        try:
            # Calculate date ranges
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_history)
            
            # Fetch historical data
            historical = self._get_historical_weather(
                latitude, longitude, start_date, end_date
            )
            
            # Fetch forecast data
            forecast = self._get_forecast_weather(latitude, longitude)
            
            # Analyze the data
            analysis = self._analyze_weather_data(historical, forecast)
            
            return {
                "historical": historical,
                "forecast": forecast,
                "analysis": analysis,
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            return self._get_fallback_weather_data()
    
    def _get_historical_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Fetch historical weather data from Open-Meteo"""
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "temperature_2m_mean",
                "precipitation_sum",
                "rain_sum",
                "et0_fao_evapotranspiration"
            ],
            "timezone": "auto"
        }
        
        try:
            response = requests.get(
                self.archive_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "dates": data.get("daily", {}).get("time", []),
                "temp_max": data.get("daily", {}).get("temperature_2m_max", []),
                "temp_min": data.get("daily", {}).get("temperature_2m_min", []),
                "temp_mean": data.get("daily", {}).get("temperature_2m_mean", []),
                "precipitation": data.get("daily", {}).get("precipitation_sum", []),
                "rain": data.get("daily", {}).get("rain_sum", []),
                "evapotranspiration": data.get("daily", {}).get("et0_fao_evapotranspiration", [])
            }
            
        except Exception as e:
            logger.error(f"Error fetching historical weather: {str(e)}")
            return {}
    
    def _get_forecast_weather(self, latitude: float, longitude: float) -> Dict:
        """Fetch 7-day weather forecast from Open-Meteo"""
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max"
            ],
            "timezone": "auto",
            "forecast_days": 7
        }
        
        try:
            response = requests.get(
                self.forecast_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "dates": data.get("daily", {}).get("time", []),
                "temp_max": data.get("daily", {}).get("temperature_2m_max", []),
                "temp_min": data.get("daily", {}).get("temperature_2m_min", []),
                "precipitation": data.get("daily", {}).get("precipitation_sum", []),
                "precipitation_probability": data.get("daily", {}).get("precipitation_probability_max", []),
                "wind_speed": data.get("daily", {}).get("wind_speed_10m_max", [])
            }
            
        except Exception as e:
            logger.error(f"Error fetching forecast: {str(e)}")
            return {}
    
    def _analyze_weather_data(self, historical: Dict, forecast: Dict) -> Dict:
        """Analyze weather data and extract insights"""
        
        analysis = {
            "total_rainfall_30d": 0,
            "avg_temperature": 0,
            "rainfall_trend": "stable",
            "forecast_rain_7d": 0,
            "temperature_stress": False,
            "drought_risk": False,
            "flood_risk": False
        }
        
        # Historical analysis
        if historical.get("precipitation"):
            rainfall = historical["precipitation"]
            analysis["total_rainfall_30d"] = sum(rainfall)
            
            # Check drought risk (less than 20mm in 30 days)
            if analysis["total_rainfall_30d"] < 20:
                analysis["drought_risk"] = True
        
        if historical.get("temp_mean"):
            temps = [t for t in historical["temp_mean"] if t is not None]
            if temps:
                analysis["avg_temperature"] = sum(temps) / len(temps)
                
                # Check temperature stress (avg > 35°C or < 10°C)
                if analysis["avg_temperature"] > 35 or analysis["avg_temperature"] < 10:
                    analysis["temperature_stress"] = True
        
        # Forecast analysis
        if forecast.get("precipitation"):
            analysis["forecast_rain_7d"] = sum(forecast["precipitation"])
            
            # Check flood risk (>100mm in next 7 days)
            if analysis["forecast_rain_7d"] > 100:
                analysis["flood_risk"] = True
        
        # Rainfall trend
        if historical.get("precipitation") and len(historical["precipitation"]) >= 14:
            recent = sum(historical["precipitation"][-7:])
            previous = sum(historical["precipitation"][-14:-7])
            
            if recent > previous * 1.5:
                analysis["rainfall_trend"] = "increasing"
            elif recent < previous * 0.5:
                analysis["rainfall_trend"] = "decreasing"
        
        return analysis
    
    def _get_fallback_weather_data(self) -> Dict:
        """Return fallback data if API fails"""
        return {
            "historical": {},
            "forecast": {},
            "analysis": {
                "total_rainfall_30d": 0,
                "avg_temperature": 25,
                "rainfall_trend": "unknown",
                "forecast_rain_7d": 0,
                "temperature_stress": False,
                "drought_risk": False,
                "flood_risk": False
            },
            "location": {},
            "error": "Weather data temporarily unavailable"
        }
