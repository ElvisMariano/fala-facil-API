"""
Health check endpoint.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connections
from django.db.utils import OperationalError
from redis import Redis
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Check the health of the application.
    """
    health_status = {
        'status': 'healthy',
        'database': True,
        'cache': True,
    }

    # Check database connection
    try:
        db_conn = connections['default']
        db_conn.cursor()
    except OperationalError:
        health_status['database'] = False
        health_status['status'] = 'unhealthy'
        logger.error('Database health check failed')

    # Check Redis connection
    try:
        redis_client = Redis.from_url(settings.CACHES['default']['LOCATION'])
        redis_client.ping()
    except Exception as e:
        health_status['cache'] = False
        health_status['status'] = 'unhealthy'
        logger.error(f'Redis health check failed: {str(e)}')

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return Response(health_status, status=status_code) 