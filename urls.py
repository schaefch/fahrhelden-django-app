from django.urls import include, path
from . import views


urlpatterns = [
    path("jobs/<int:pk>/", views.JobAlterView.as_view()),
    path("jobs/", views.JobsListView.as_view()),
    path(
        "auth_web/", include("rest_framework.urls", namespace="rest_framework")
    ),
]
