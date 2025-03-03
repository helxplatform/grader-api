import logging
from fastapi_events.dispatcher import dispatch as _dispatch

logger = logging.getLogger(__file__)

def dispatch(*args, **kwargs):
    try: _dispatch(*args, **kwargs)
    except LookupError:
        # Running outside FastAPI context
        logger.info("Outside app context, skipping dispatch for ", args, kwargs)