"""
Satellite Service - Google Earth Engine Integration
Fetches Sentinel-2 data and calculates vegetation indices (NDVI, NDMI)
"""

import ee
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)


class SatelliteService:
    """Service to fetch and analyze Sentinel-2 satellite data"""
    
    def __init__(self):
        self.initialized = False
        self.service_account_key = None
    
    def initialize(self):
        """Initialize Google Earth Engine authentication"""
        try:
            # Try to authenticate with service account
            credentials_path = os.environ.get('GEE_CREDENTIALS_PATH', 'gee-credentials.json')
            
            if os.path.exists(credentials_path):
                # Service account authentication
                credentials = ee.ServiceAccountCredentials(
                    email=None,  # Will be read from JSON
                    key_file=credentials_path
                )
                ee.Initialize(credentials, project="farmmonitor-486009")
                logger.info("GEE initialized with service account")
            else:
                # Try default authentication (for development)
                try:
                    ee.Initialize(project="farmmonitor-486009")
                    logger.info("GEE initialized with default credentials")
                except Exception as e:
                    logger.warning(f"GEE initialization failed: {str(e)}")
                    logger.warning("Satellite features will use mock data")
                    return
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing Google Earth Engine: {str(e)}")
            logger.warning("Satellite features will use mock data")
    
    def is_initialized(self) -> bool:
        """Check if GEE is initialized"""
        return self.initialized
    
    async def get_ndvi_analysis(
        self,
        polygon_coords: List,
        center_lat: float,
        center_lng: float,
        days_back: int = 30
    ) -> Dict:
        """
        Get NDVI analysis for a farm polygon
        
        Args:
            polygon_coords: Polygon coordinates in GeoJSON format
            center_lat: Center latitude
            center_lng: Center longitude
            days_back: Number of days to look back for imagery
            
        Returns:
            Dictionary with NDVI analysis
        """
        
        if not self.initialized:
            logger.warning("GEE not initialized, returning mock data")
            return self._get_mock_satellite_data()
        
        try:
            # Convert polygon to Earth Engine geometry
            polygon = self._coords_to_ee_polygon(polygon_coords)
            
            # Define date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Get Sentinel-2 image collection
            collection = ee.ImageCollection('COPERNICUS/S2_SR') \
                .filterBounds(polygon) \
                .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                .sort('CLOUDY_PIXEL_PERCENTAGE')
            
            # Get the least cloudy image
            image = collection.first()
            
            # Check if image exists
            image_info = image.getInfo()
            if image_info is None:
                logger.warning("No satellite imagery found for this location/date")
                return self._get_mock_satellite_data()
            
            # Calculate NDVI
            ndvi = self._calculate_ndvi(image)
            
            # Calculate NDMI (Moisture Index)
            ndmi = self._calculate_ndmi(image)
            
            # Get statistics for the polygon
            ndvi_stats = self._get_statistics(ndvi, polygon)
            ndmi_stats = self._get_statistics(ndmi, polygon)
            
            # Get image metadata
            metadata = {
                'acquisition_date': image.get('system:time_start').getInfo(),
                'cloud_cover': image.get('CLOUDY_PIXEL_PERCENTAGE').getInfo(),
                'satellite': 'Sentinel-2'
            }
            
            return {
                'ndvi_mean': ndvi_stats.get('mean'),
                'ndvi_min': ndvi_stats.get('min'),
                'ndvi_max': ndvi_stats.get('max'),
                'ndvi_std': ndvi_stats.get('std'),
                'ndmi_mean': ndmi_stats.get('mean'),
                'ndmi_min': ndmi_stats.get('min'),
                'ndmi_max': ndmi_stats.get('max'),
                'metadata': metadata,
                'health_category': self._categorize_ndvi(ndvi_stats.get('mean'))
            }
            
        except Exception as e:
            logger.error(f"Error fetching satellite data: {str(e)}")
            return self._get_mock_satellite_data()
    
    def _coords_to_ee_polygon(self, coords: List) -> ee.Geometry.Polygon:
        """Convert GeoJSON coordinates to Earth Engine polygon"""
        # GeoJSON format: [[[lng, lat], [lng, lat], ...]]
        # Earth Engine expects: [[lng, lat], [lng, lat], ...]
        polygon_coords = coords[0]  # Extract first ring
        return ee.Geometry.Polygon(polygon_coords)
    
    def _calculate_ndvi(self, image: ee.Image) -> ee.Image:
        """
        Calculate NDVI (Normalized Difference Vegetation Index)
        NDVI = (NIR - Red) / (NIR + Red)
        """
        nir = image.select('B8')  # Near-Infrared band
        red = image.select('B4')  # Red band
        
        ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
        return ndvi
    
    def _calculate_ndmi(self, image: ee.Image) -> ee.Image:
        """
        Calculate NDMI (Normalized Difference Moisture Index)
        NDMI = (NIR - SWIR) / (NIR + SWIR)
        """
        nir = image.select('B8')   # Near-Infrared band
        swir = image.select('B11') # Shortwave Infrared band
        
        ndmi = nir.subtract(swir).divide(nir.add(swir)).rename('NDMI')
        return ndmi
    
    def _get_statistics(self, image: ee.Image, geometry: ee.Geometry) -> Dict:
        """Get statistical values for an image within a geometry"""
        try:
            stats = image.reduceRegion(
                reducer=ee.Reducer.mean().combine(
                    reducer2=ee.Reducer.minMax(),
                    sharedInputs=True
                ).combine(
                    reducer2=ee.Reducer.stdDev(),
                    sharedInputs=True
                ),
                geometry=geometry,
                scale=10,  # 10m resolution for Sentinel-2
                maxPixels=1e9
            ).getInfo()
            
            # Extract values (band name depends on the image)
            band_name = list(stats.keys())[0].split('_')[0]
            
            return {
                'mean': stats.get(f'{band_name}_mean'),
                'min': stats.get(f'{band_name}_min'),
                'max': stats.get(f'{band_name}_max'),
                'std': stats.get(f'{band_name}_stdDev')
            }
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            return {'mean': None, 'min': None, 'max': None, 'std': None}
    
    def _categorize_ndvi(self, ndvi_value: Optional[float]) -> str:
        """Categorize crop health based on NDVI value"""
        if ndvi_value is None:
            return "Unknown"
        
        if ndvi_value > 0.6:
            return "Excellent"
        elif ndvi_value > 0.4:
            return "Good"
        elif ndvi_value > 0.3:
            return "Moderate"
        elif ndvi_value > 0.2:
            return "Poor"
        else:
            return "Very Poor"
    
    def _get_mock_satellite_data(self) -> Dict:
        """Return mock satellite data when GEE is unavailable"""
        import random
        
        # Generate realistic mock data
        ndvi_mean = random.uniform(0.4, 0.7)
        
        return {
            'ndvi_mean': round(ndvi_mean, 3),
            'ndvi_min': round(ndvi_mean - 0.1, 3),
            'ndvi_max': round(ndvi_mean + 0.1, 3),
            'ndvi_std': round(random.uniform(0.05, 0.15), 3),
            'ndmi_mean': round(random.uniform(0.2, 0.5), 3),
            'ndmi_min': round(random.uniform(0.1, 0.3), 3),
            'ndmi_max': round(random.uniform(0.4, 0.6), 3),
            'metadata': {
                'acquisition_date': int(datetime.now().timestamp() * 1000),
                'cloud_cover': random.uniform(5, 15),
                'satellite': 'Sentinel-2 (Mock Data)'
            },
            'health_category': self._categorize_ndvi(ndvi_mean),
            'mock_data': True
        }
