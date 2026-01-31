"""
Farm Monitor API - Main Application
Zero-cost farm monitoring with satellite & weather analysis
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import logging
import os

# Import services
from services.weather import WeatherService
from services.satellite import SatelliteService
from services.analysis import AgronomicAnalyzer
from services.pdf_gen import PDFGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Farm Monitor API",
    description="Satellite health & weather analysis for farms",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================
# Data Models
# ===========================

class PolygonCoordinates(BaseModel):
    type: str = Field(default="Polygon")
    coordinates: List[List[List[float]]]

    @field_validator("coordinates", mode="before")
    @classmethod
    def normalize_coordinates(cls, v: object) -> List[List[List[float]]]:
        """Accept [[[lng,lat],...]] or single ring [[lng,lat],...]; always return array of rings."""
        if not isinstance(v, list) or not v:
            return v
        first = v[0]
        # Single ring: [[lng,lat], [lng,lat], ...] -> first element is a point (list of 2 numbers)
        if isinstance(first, list) and len(first) >= 2 and isinstance(first[0], (int, float)):
            return [v]
        return v

class CenterPoint(BaseModel):
    lat: float
    lng: float

class FarmReportRequest(BaseModel):
    farm_name: str = Field(..., min_length=1, max_length=100)
    crop_type: str = Field(..., min_length=1)
    email: Optional[str] = None
    planting_date: Optional[str] = None
    polygon: PolygonCoordinates
    area: float = Field(..., gt=0)
    center: CenterPoint

class FarmReportResponse(BaseModel):
    farm_name: str
    crop_type: str
    area: float
    ndvi_value: Optional[float] = None
    health_status: str
    recommendations: str
    pdf_url: Optional[str] = None
    pdf_base64: Optional[str] = None

# ===========================
# Service Initialization
# ===========================

weather_service = WeatherService()
satellite_service = SatelliteService()
analyzer = AgronomicAnalyzer()
pdf_generator = PDFGenerator()

# ===========================
# Routes
# ===========================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "app": "Farm Monitor API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/api/health",
            "generate_report": "/api/generate-report"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "weather": "available",
            "satellite": "available" if satellite_service.is_initialized() else "initializing",
            "pdf": "available"
        }
    }

@app.post("/api/generate-report", response_model=FarmReportResponse)
async def generate_report(request: FarmReportRequest, background_tasks: BackgroundTasks):
    """
    Generate farm monitoring report with satellite and weather data
    """
    try:
        logger.info(f"Generating report for farm: {request.farm_name}")
        
        # Extract coordinates
        center_lat = request.center.lat
        center_lng = request.center.lng
        polygon_coords = request.polygon.coordinates
        
        # 1. Fetch Weather Data
        logger.info("Fetching weather data...")
        weather_data = await weather_service.get_weather_analysis(
            latitude=center_lat,
            longitude=center_lng
        )
        
        # 2. Fetch Satellite Data and Calculate NDVI
        logger.info("Fetching satellite data...")
        satellite_data = await satellite_service.get_ndvi_analysis(
            polygon_coords=polygon_coords,
            center_lat=center_lat,
            center_lng=center_lng
        )
        
        # 3. Perform Agronomic Analysis
        logger.info("Analyzing data...")
        analysis = analyzer.analyze(
            weather_data=weather_data,
            satellite_data=satellite_data,
            crop_type=request.crop_type,
            planting_date=request.planting_date,
            area=request.area
        )
        
        # 4. Generate PDF Report
        logger.info("Generating PDF...")
        pdf_result = pdf_generator.generate_report(
            farm_name=request.farm_name,
            crop_type=request.crop_type,
            area=request.area,
            center={'lat': center_lat, 'lng': center_lng},
            weather_data=weather_data,
            satellite_data=satellite_data,
            analysis=analysis
        )
        
        # 5. Prepare response
        response = FarmReportResponse(
            farm_name=request.farm_name,
            crop_type=request.crop_type,
            area=request.area,
            ndvi_value=satellite_data.get('ndvi_mean'),
            health_status=analysis.get('health_status', 'Good'),
            recommendations=analysis.get('recommendations', ''),
            pdf_base64=pdf_result.get('pdf_base64')
        )
        
        logger.info(f"Report generated successfully for {request.farm_name}")
        
        # Send email in background if provided
        if request.email:
            background_tasks.add_task(
                send_email_report,
                email=request.email,
                pdf_base64=pdf_result.get('pdf_base64'),
                farm_name=request.farm_name
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )

@app.get("/api/download/{filename}")
async def download_report(filename: str):
    """Download generated PDF report"""
    file_path = f"/tmp/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf"
    )

# ===========================
# Background Tasks
# ===========================

async def send_email_report(email: str, pdf_base64: str, farm_name: str):
    """
    Send email with PDF report (placeholder)
    In production, integrate with SendGrid, Mailgun, or similar
    """
    logger.info(f"Would send email to {email} for farm {farm_name}")
    # TODO: Implement email sending
    pass

# ===========================
# Run Application
# ===========================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
