from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .serializers import RegisterSerializer, LoginSerializer
from .utils import generate_otp_for_user, send_otp_via_email



class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            # Save the user to database
            user = serializer.save()

            # Generate and store OTP
            otp = generate_otp_for_user(user)

            # Send OTP email
            send_otp_via_email(user.email, otp)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            # Authenticate user
            user = authenticate(request, email=email, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token

                return Response(
                    {
                        "access_token": str(access_token),
                        "refresh_token": str(refresh),
                        "user_name": user.name,
                    },
                    status=status.HTTP_200_OK,
                )

            # Return error message if authentication fails
            return Response(
                {"message": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return error if serializer data is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
