from typing import Dict, Any
import time
from datetime import datetime
import psutil
from config import settings
from utils import logger
from database import db

class MetricsCollector:
    """Collects and stores system and application metrics."""
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.start_time = time.time()
        self.metrics = {
            "system": {},
            "application": {},
            "api_calls": {},
            "errors": []
        }

    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return {}

    def collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application-level metrics."""
        try:
            uptime = time.time() - self.start_time
            return {
                "uptime": uptime,
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error collecting application metrics: {str(e)}")
            return {}

    def log_api_call(self, service: str, endpoint: str, status: str) -> None:
        """Log an API call."""
        try:
            key = f"{service}:{endpoint}"
            if key not in self.metrics["api_calls"]:
                self.metrics["api_calls"][key] = {
                    "total": 0,
                    "success": 0,
                    "error": 0
                }
            self.metrics["api_calls"][key]["total"] += 1
            if status == "success":
                self.metrics["api_calls"][key]["success"] += 1
            else:
                self.metrics["api_calls"][key]["error"] += 1
        except Exception as e:
            logger.error(f"Error logging API call: {str(e)}")

    def log_error(self, error: Exception, context: str) -> None:
        """Log an error."""
        try:
            self.metrics["errors"].append({
                "error": str(error),
                "context": context,
                "timestamp": datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Error logging error: {str(e)}")

    def save_metrics(self) -> None:
        """Save metrics to the database."""
        try:
            metrics_data = {
                "system": self.collect_system_metrics(),
                "application": self.collect_application_metrics(),
                "api_calls": self.metrics["api_calls"],
                "errors": self.metrics["errors"],
                "timestamp": datetime.utcnow()
            }
            
            db.db.metrics.insert_one(metrics_data)
            logger.info("Saved metrics to database")
            
            # Clear error logs after saving
            self.metrics["errors"] = []
        except Exception as e:
            logger.error(f"Error saving metrics: {str(e)}")

# Create global metrics collector instance
metrics_collector = MetricsCollector() 