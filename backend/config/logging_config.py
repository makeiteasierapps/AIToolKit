import os
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )

    # Set specific level for our application loggers
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.DEBUG if os.getenv("IS_LOCAL_DEV", "false") == "true" else logging.INFO)

    # Set higher level for third-party libraries
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('fastapi').setLevel(logging.WARNING)
    logging.getLogger('LiteLLM').setLevel(logging.WARNING)

    return logging.getLogger('app.main')