from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Job, Bringer
import djoser.serializers
from django.db import IntegrityError, transaction
from django.core import exceptions as django_exceptions
from djoser.conf import settings


class JobAlterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            "id",
            "status",
            "drivers_comment",
        )


class JobOverviewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            "id",
            "location",
            "zip_code",
            "placed_at",
            "amount",
        )


class JobDetailedListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            "id",
            "first_name",
            "last_name",
            "street",
            "house_nr",
            "location",
            "zip_code",
            "placed_at",
            "buy_list",
            "amount",
            "status",
            "drivers_comment",
            "phone_number",
        )


class CustomUserCreateSerializer(djoser.serializers.UserCreateSerializer):
    class Meta(djoser.serializers.UserCreateSerializer.Meta):
        model = Bringer
        fields = (
            "email",
            "password",
            "first_name",
            "last_name",
            "street",
            "house_nr",
            "zip_code",
            "location",
            "phone_number",
            "birth_date",
        )

    def validate(self, attrs):
        user = self.Meta.model(**attrs)
        password = attrs.get("password")

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )

        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")

        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = self.Meta.model.objects.create_user(**validated_data)
            if settings.SEND_ACTIVATION_EMAIL:
                user.is_active = False
                user.save(update_fields=["is_active"])
        return user
