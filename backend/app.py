from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.middleware.errors import (
    service_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from backend.routes import analysis, health, report, upload
from backend.services.exceptions import ServiceError


settings.ensure_storage_dirs()

app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(ServiceError, service_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

app.include_router(health.router)
app.include_router(upload.router)
app.include_router(analysis.router)
app.include_router(report.router)
