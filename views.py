from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, BasePermission
from . import serializers
from .models import Job
import djoser.views


class IsConfirmedBringer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_active and request.user.is_confirmed


class PosessesJob(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.driver.id == request.user.id


class CanListJob(PosessesJob):
    def has_object_permission(self, request, view, obj):
        return (
            super().has_object_permission(request, view, obj)
            or obj.driver is None
        )


class CanAlterJob(PosessesJob):
    def has_object_permission(self, request, view, obj):
        return (
            super().has_object_permission(request, view, obj)
            or obj.driver is None
        ) and obj.status != "DONE"


class JobsListView(generics.ListAPIView):
    permission_classes = [
        IsConfirmedBringer,
        CanListJob,
    ]

    def get_queryset(self):
        status = self.request.query_params.get("status", "WAITING")
        objects = Job.objects.filter(status=status).order_by("placed_at")
        if status == "WAITING":
            return objects
        elif status == "PENDING":
            return objects.filter(driver_id=self.request.user.id)
        else:
            return objects.filter(driver_id=self.request.user.id).order_by(
                "-placed_at"
            )

    def get_serializer_class(self):
        status = self.request.query_params.get("status", "WAITING")
        if status == "PENDING":
            return serializers.JobDetailedListSerializer
        else:
            return serializers.JobOverviewListSerializer


class JobAlterView(generics.RetrieveAPIView, generics.UpdateAPIView):
    queryset = Job.objects.all()
    serializer_class = serializers.JobAlterSerializer
    permission_classes = [
        IsAuthenticated,
        IsConfirmedBringer,
        CanAlterJob,
    ]

    def update(self, request, *args, **kwargs):
        if request.data["status"] == "WAITING":
            # Clear drivers comment
            request.data._mutable = True
            request.data["drivers_comment"] = ""
        return super().update(request, *args, **kwargs)


class TokenCreateView(djoser.views.TokenCreateView):
    permission_classes = [
        IsAuthenticated,
        IsConfirmedBringer,
    ]
