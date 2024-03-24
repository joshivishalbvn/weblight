import datetime
from .models import SmsOtp
from .task import send_otp , send_email
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from base.permissions import UserRolePermission
from .utils import create_otp, get_lead_filter_params
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate , get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .serializers import PasswordResetSerializer, UserSerializer

User = get_user_model()

class UserRegistration(APIView):
    """
    API endpoint for user registration.

    This endpoint allows users to register by providing necessary details.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST request for user registration.

        This method accepts a POST request with user details and creates a new user account if the provided data is valid.

        Args:
            request: HTTP POST request containing user registration data.

        Returns:
            Response: HTTP response indicating the success or failure of the registration attempt.
        """
        print(request.data)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignInView(APIView):
    """
    API endpoint for user sign-in.

    This endpoint allows users to sign in by providing their phone number and receiving an OTP for authentication.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data['phone_number']
        try:
            user = User.objects.get(phone_number__iexact=phone_number)
        except User.DoesNotExist:
            return Response({'error': 'User with this phone number does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        otp = create_otp()
        SmsOtp.delete_by_sms(user)
        SmsOtp.objects.create(user=user, otp=otp)
        # send_otp_email.delay(user.email, otp)
        send_otp(user.phone_number, otp)
        return Response({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)

        

class AuthenticateUserView(APIView):
    """
    Authenticate User View
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST request for user sign-in.

        This method accepts a POST request with a user's phone number and sends an OTP to that number for authentication.

        Args:
            request: HTTP POST request containing user's phone number.

        Returns:
            Response: HTTP response indicating the success or failure of the sign-in attempt.
        """
        phone_number = request.data['phone_number']
        otp = request.data['otp']
        try:
            user_obj = User.objects.get(phone_number__iexact=phone_number)
        except User.DoesNotExist:
            return Response({'error': 'Invalid Phone Number.'}, status=status.HTTP_404_NOT_FOUND)
        otp_obj = SmsOtp.objects.get(user=user_obj, otp=otp)
        print('\033[91m'+'otp_obj: ' + '\033[92m', otp_obj.otp)
        print('\033[91m'+'otp: ' + '\033[92m', otp)
        if int(otp) == int(otp_obj.otp):
            user = authenticate(username=user_obj.get_username())
            refresh = RefreshToken.for_user(user_obj)
            SmsOtp.delete_by_sms(phone_number)
            data = {
                "token": str(refresh.access_token),
                "refresh": str(refresh),
                "message": "User Login successfull",
                "access_token_expiry": str(datetime.datetime.now() + refresh.access_token.lifetime),
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)
        

class PasswordResetRequestView(APIView):
    """
    API endpoint for requesting password reset.

    This endpoint allows users to request a password reset by providing their email address.
    """
    
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST request for password reset request.

        This method accepts a POST request with user's email address and initiates the password reset process.

        Args:
            request: HTTP POST request containing user's email address.

        Returns:
            Response: HTTP response indicating the success or failure of the password reset request.
        """
        email = request.data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        print('\033[91m'+'token: ' + '\033[92m', token)
        user.reset_password_token = token
        user.save()
        reset_link = reverse('users:reset_password', kwargs={'token': token})
        send_email(user.email,reset_link)
        return Response({'message': 'Password reset email sent successfully.'}, status=status.HTTP_200_OK)
        


class PasswordResetView(APIView):
    """
    API endpoint for resetting password.

    This endpoint allows users to reset their password by providing a new password along with a token received via email.
    """
    permission_classes = [AllowAny]

    def post(self, request,token):
        """
        Handle POST request for password reset.

        This method accepts a POST request with a new password and a token received via email, and resets the user's password.

        Args:
            request: HTTP POST request containing new password.
            token: Token received via email.

        Returns:
            Response: HTTP response indicating the success or failure of the password reset attempt.
        """
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(reset_password_token=token)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            user.set_password(password)
            user.save()
            return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD API endpoint for managing users.

    This endpoint provides CRUD operations for managing user accounts.
    """

    permission_classes = [UserRolePermission]
    serializer_class = UserSerializer

    def get_queryset(self):
        """
        Get queryset for user data.

        This method returns the queryset containing user data filtered based on query parameters.

        Returns:
            Queryset: Filtered queryset containing user data
        """
        queryset = User.objects.all().order_by("id")
        page_items = self.request.query_params.get("page_items")
        query_params = self.request.query_params
        if page_items:
            self.pagination_class.page_size = int(page_items)
        if query_params:
            queryset = queryset.filter(get_lead_filter_params(query_params))
        return queryset