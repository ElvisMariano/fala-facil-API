"""Core utilities."""
from typing import Any, Dict, Optional
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


class CustomJSONEncoder(DjangoJSONEncoder):
    """Custom JSON encoder that can handle Python types."""

    def default(self, obj: Any) -> Any:
        """Handle special Python types."""
        # Handle type objects (classes)
        if isinstance(obj, type):
            return str(obj.__name__)
        # Handle callables
        elif callable(obj):
            return str(obj.__name__)
        # Handle dataclasses, models, etc.
        elif hasattr(obj, "__dict__"):
            return str(obj)
        # Handle other special types
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


class CustomJSONRenderer(JSONRenderer):
    """Custom JSON renderer that uses our CustomJSONEncoder."""
    
    encoder_class = CustomJSONEncoder


class CustomSchemaAPIView(APIView):
    """Custom API view for generating OpenAPI schema with proper type handling."""
    
    renderer_classes = [CustomJSONRenderer]
    
    def get(self, request, *args, **kwargs):
        """Generate and return the API schema with proper type handling."""
        # Import here to avoid circular imports
        from drf_spectacular.generators import SchemaGenerator
        from drf_spectacular.settings import spectacular_settings
        
        # Use the default SchemaGenerator
        generator = SchemaGenerator(
            urlconf=getattr(spectacular_settings, 'SERVE_URLCONF', None),
            api_version=request.GET.get('api_version', None)
        )
        schema = generator.get_schema(request=request, public=True)
        
        # Process schema to convert type objects to strings
        def process_schema(obj: Any) -> Any:
            if isinstance(obj, type):
                return str(obj.__name__)
            elif isinstance(obj, dict):
                return {k: process_schema(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [process_schema(i) for i in obj]
            return obj
        
        processed_schema = process_schema(schema)
        
        if "format" in request.GET and request.GET["format"] == "yaml":
            return Response({"error": "YAML format unavailable for custom schema"})
        
        return Response(processed_schema) 