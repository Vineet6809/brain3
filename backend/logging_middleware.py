import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Create logs directory
logs_dir = Path("/var/log/app")
logs_dir.mkdir(parents=True, exist_ok=True)

# Configure comprehensive logging
class ComprehensiveLogger:
    def __init__(self):
        self.setup_loggers()
    
    def setup_loggers(self):
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        json_formatter = logging.Formatter(
            '%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Main application logger
        self.app_logger = logging.getLogger('app')
        self.app_logger.setLevel(logging.INFO)
        
        # Create rotating file handler for main logs (10MB max, 5 backups)
        app_handler = RotatingFileHandler(
            logs_dir / 'app_events.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        app_handler.setFormatter(detailed_formatter)
        self.app_logger.addHandler(app_handler)
        
        # Request logger for all HTTP requests
        self.request_logger = logging.getLogger('requests')
        self.request_logger.setLevel(logging.INFO)
        
        request_handler = RotatingFileHandler(
            logs_dir / 'requests.log',
            maxBytes=10*1024*1024,
            backupCount=5
        )
        request_handler.setFormatter(json_formatter)
        self.request_logger.addHandler(request_handler)
        
        # Error logger for all errors
        self.error_logger = logging.getLogger('errors')
        self.error_logger.setLevel(logging.ERROR)
        
        error_handler = RotatingFileHandler(
            logs_dir / 'errors.log',
            maxBytes=10*1024*1024,
            backupCount=5
        )
        error_handler.setFormatter(detailed_formatter)
        self.error_logger.addHandler(error_handler)
        
        # Performance logger
        self.perf_logger = logging.getLogger('performance')
        self.perf_logger.setLevel(logging.INFO)
        
        perf_handler = RotatingFileHandler(
            logs_dir / 'performance.log',
            maxBytes=10*1024*1024,
            backupCount=5
        )
        perf_handler.setFormatter(json_formatter)
        self.perf_logger.addHandler(perf_handler)

# Initialize logger
comprehensive_logger = ComprehensiveLogger()

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests and outgoing responses
    """
    
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Get request details
        request_details = {
            'timestamp': datetime.utcnow().isoformat(),
            'method': request.method,
            'url': str(request.url),
            'path': request.url.path,
            'query_params': dict(request.query_params),
            'client_host': request.client.host if request.client else 'unknown',
            'headers': dict(request.headers)
        }
        
        # Log incoming request
        comprehensive_logger.app_logger.info(
            f"Incoming request: {request.method} {request.url.path}"
        )
        
        comprehensive_logger.request_logger.info(
            json.dumps({
                'type': 'request',
                **request_details
            })
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate request duration
            duration = time.time() - start_time
            
            # Log response
            response_details = {
                'timestamp': datetime.utcnow().isoformat(),
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'client_host': request.client.host if request.client else 'unknown'
            }
            
            comprehensive_logger.app_logger.info(
                f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration*1000:.2f}ms"
            )
            
            comprehensive_logger.request_logger.info(
                json.dumps({
                    'type': 'response',
                    **response_details
                })
            )
            
            # Log slow requests (> 1 second)
            if duration > 1.0:
                comprehensive_logger.perf_logger.warning(
                    json.dumps({
                        'type': 'slow_request',
                        'path': request.url.path,
                        'method': request.method,
                        'duration_ms': round(duration * 1000, 2)
                    })
                )
            
            # Log error responses
            if response.status_code >= 400:
                comprehensive_logger.error_logger.error(
                    f"Error response: {request.method} {request.url.path} - Status: {response.status_code} - Client: {request.client.host if request.client else 'unknown'}"
                )
            
            return response
            
        except Exception as e:
            # Calculate request duration
            duration = time.time() - start_time
            
            # Log exception
            comprehensive_logger.error_logger.error(
                f"Exception in request: {request.method} {request.url.path} - Error: {str(e)}",
                exc_info=True
            )
            
            comprehensive_logger.request_logger.error(
                json.dumps({
                    'type': 'exception',
                    'timestamp': datetime.utcnow().isoformat(),
                    'method': request.method,
                    'path': request.url.path,
                    'error': str(e),
                    'duration_ms': round(duration * 1000, 2)
                })
            )
            
            # Re-raise the exception
            raise
