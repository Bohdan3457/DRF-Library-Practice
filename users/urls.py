from django.urls import path
from users.views import CreateUserView, ManageUserView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

app_name = "users"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", ManageUserView.as_view(), name="manage")
]
