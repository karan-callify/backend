import logging
import datetime
import contextvars
from typing import Optional
from pythonjsonlogger import jsonlogger
from app.db.mongo_session import get_mongo_db

# Context variables to hold the request_id and job_id
request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_id", default=None)
job_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("job_id", default=None)

class MongoDBLogHandler(logging.Handler):
    """Custom log handler that buffers logs per request and writes them to MongoDB at the end."""
    def __init__(self):
        super().__init__()
        self.buffer = {}

    def emit(self, record):
        try:
            req_id = request_id_ctx.get()
            if not req_id:
                return

            job_id = job_id_ctx.get()

            log_entry = {
                "level": record.levelname,
                "message": record.getMessage(),
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }

            # include job_id if present
            if job_id:
                log_entry["job_id"] = job_id

            if req_id not in self.buffer:
                self.buffer[req_id] = []
            self.buffer[req_id].append(log_entry)
        except Exception:
            self.handleError(record)

    async def flush_request_logs(self, request_id, request_meta):
        """Save buffered logs for a specific request to MongoDB."""
        logs = self.buffer.pop(request_id, [])
        if logs:
            db = get_mongo_db()
            collection = db["api_logs"]
            # collect job_id from context (may be same across logs but prefer explicit)
            job_id = job_id_ctx.get()

            doc = {
                "request_id": request_id,
                "job_id": job_id,
                "path": request_meta.get("path"),
                "method": request_meta.get("method"),
                "status_code": request_meta.get("status_code"),
                "logs": logs,
                "created_at": datetime.datetime.utcnow(),
            }
            await collection.insert_one(doc)

# Configure global logger
logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

# Console JSON handler
stream_handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(message)s")
stream_handler.setFormatter(formatter)

# Mongo handler
mongo_handler = MongoDBLogHandler()

# expose for middleware
__all__ = ["logger", "request_id_ctx", "job_id_ctx", "mongo_handler"]

logger.addHandler(stream_handler)
logger.addHandler(mongo_handler)
