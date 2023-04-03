import structlog
from waitress import serve

from app import subscriber, cloud_config

logger = structlog.get_logger()


if __name__ == '__main__':
    logger.info('Starting SDX SEFT')
    cloud_config()
    serve(subscriber, host='0.0.0.0', port=5000)
