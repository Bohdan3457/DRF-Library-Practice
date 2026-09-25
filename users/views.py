from rest_framework import generics, permissions
from users.serializers import UserRegistrationSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
