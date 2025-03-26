"""Views for users app."""

from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import (ChangePasswordSerializer, UserSerializer,
                        UserUpdateSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user model."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Return appropriate permissions."""
        if self.action in ['create']:
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return self.serializer_class

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Return current user."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT) 