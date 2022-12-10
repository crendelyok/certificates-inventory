import logging

from fastapi import HTTPException, Request

logging.getLogger(__name__)


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as h_exc:
        raise h_exc
    except Exception as exc:
        logging.critical(
            "Unhandled exception on request %s %s %s %s: %s",
            request.method,
            request.url,
            request.query_params,
            await request.body(),
            str(exc),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error") from exc
