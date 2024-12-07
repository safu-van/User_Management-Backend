from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model

from .serializers import RegisterSerializer, LoginSerializer, OTPSerializer
from .utils import generate_otp_for_user, send_otp_via_email


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the user to database
        user = serializer.save()

        # Generate and store OTP
        otp = generate_otp_for_user(user)

        # Send OTP email
        send_otp_via_email(user.email, otp)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # Authenticate user
        user = authenticate(email=email, password=password)
        if user and user.is_verified:
            # Generate tokens for the user
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


User = get_user_model()


class SendOTPView(APIView):
    def post(self, request):
        serializer = OTPSerializer(data=request.data, context={"otp_field": False})
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"message": "User account not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Generate and store OTP
        otp = generate_otp_for_user(user)

        # Send OTP email
        send_otp_via_email(user.email, otp)

        return Response(
            {"message": "OTP sented successfully"}, status=status.HTTP_200_OK
        )


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPSerializer(data=request.data, context={"otp_field": True})
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        # Fetch user with associated OTP
        user = User.objects.select_related("userotp").filter(email=email).first()

        if not user:
            return Response(
                {"message": "User account not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_otp = user.userotp

        # Validate OTP
        if user_otp.otp != otp:
            return Response(
                {"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        if user_otp.is_expired():
            user_otp.delete()
            return Response(
                {"message": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Mark user as verified
        user.is_verified = True
        user.save()
        user_otp.delete()

        # Generate tokens for the user
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
