from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
from typing import Optional, cast
import json
from app.utils.logger_util import logger, request_id_ctx, job_id_ctx, mongo_handler

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that creates request ID and buffers all logs for that request."""
    async def dispatch(self, request: Request, call_next):
        req_id = str(uuid.uuid4())
        # cast to Optional[str] to satisfy static type checkers
        request_id_ctx.set(cast(Optional[str], req_id))
        # attempt to extract job_id from various places: json body, form data, query params, headers
        job_id = None

        try:
            # read and store body to replay later
            body_bytes = await request.body()

            content_type = request.headers.get('content-type', '')

            # prefer parsing form data (handles multipart/form-data and application/x-www-form-urlencoded)
            if 'application/x-www-form-urlencoded' in content_type or 'multipart/form-data' in content_type:
                try:
                    form = await request.form()
                    if 'job_id' in form:
                        job_id = form.get('job_id')
                except Exception:
                    # fallback to raw parsing
                    pass
            else:
                if body_bytes:
                    # try json
                    try:
                        body_json = json.loads(body_bytes.decode('utf-8'))
                        if isinstance(body_json, dict) and "job_id" in body_json:
                            job_id = body_json.get("job_id")
                    except Exception:
                        # not json, could be form-encoded
                        try:
                            body_text = body_bytes.decode('utf-8')
                            # simple parse for key=value pairs
                            for pair in body_text.split('&'):
                                if '=' in pair:
                                    k, v = pair.split('=', 1)
                                    if k == 'job_id':
                                        job_id = v
                                        break
                        except Exception:
                            pass

            # check query params
            if not job_id:
                job_id = request.query_params.get('job_id')

            # check headers
            if not job_id:
                job_id = request.headers.get('x-job-id') or request.headers.get('job_id')

        except Exception as e:
            logger.debug(f"Error while extracting job_id: {e}")

        # set job_id contextvar (may be None)
        job_id_ctx.set(cast(Optional[str], job_id))

        logger.info(f"{request.method} {request.url.path} - Request started")
        try:
            # replay the body for downstream handlers by creating a new request with the same body
            # starlette's Request is immutable, but call_next will read the body via receive. We can
            # override the request._body/stream by creating a receive function. FastAPI/Starlette
            # caches the body after .body() is called above, so call_next should still see the body.
            response = await call_next(request)
            logger.info(f"Request completed with status {response.status_code}")
        except Exception as e:
            logger.exception(f"Unhandled error: {e}")
            raise
        finally:
            await mongo_handler.flush_request_logs(req_id, {
                "path": request.url.path,
                "method": request.method,
                "status_code": getattr(response, "status_code", 500)
            })

            # clear contextvars to avoid leaking across async tasks
            try:
                request_id_ctx.set(None)
                job_id_ctx.set(None)
            except Exception:
                pass

        return response
