"""Serializers for users app."""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user model."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        """Meta options."""

        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'password2',
            'avatar',
            'bio',
            'language',
            'level',
            'experience',
            'streak',
            'last_activity',
            'is_premium',
            'date_joined',
        ]
        read_only_fields = [
            'id',
            'level',
            'experience',
            'streak',
            'last_activity',
            'is_premium',
            'date_joined',
        ]

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password': 'As senhas não conferem.',
            })
        return attrs

    def create(self, validated_data):
        """Create user with encrypted password."""
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """Update user."""
        password = validated_data.pop('password', None)
        password2 = validated_data.pop('password2', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password and password2:
            instance.set_password(password)

        instance.save()
        return instance


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user."""

    class Meta:
        """Meta options."""

        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'bio',
            'language',
            'level',
            'experience',
            'streak',
            'last_activity',
            'is_premium',
            'date_joined',
        ]
        read_only_fields = [
            'id',
            'level',
            'experience',
            'streak',
            'last_activity',
            'is_premium',
            'date_joined',
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('A senha atual está incorreta.')
        return value

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                'new_password': 'As senhas não conferem.',
            })
        return attrs

    def save(self, **kwargs):
        """Save new password."""
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user 