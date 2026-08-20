from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import check_password
from .models import Organization, User
from .serializers import LoginSerializer, ChangePasswordSerializer, UserSerializer

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Invalid data', 'errors': serializer.errors},
                          status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        role = serializer.validated_data.get('role', 'student')

        user = None
        org = None
        org_id = None

        if role == 'support':
            # Support account
            try:
                user = User.objects.get(username=username, role='support')
                if user.check_password(password):
                    org = None
                else:
                    user = None
            except User.DoesNotExist:
                pass

        elif role == 'ceo':
            # CEO or Staff (Admin/Manager/Teacher)
            try:
                org = Organization.objects.get(username=username)
                if org.check_password(password):
                    user = None  # CEO uses org directly
                    org_id = org.id
                else:
                    org = None
            except Organization.DoesNotExist:
                pass

            if not org:
                try:
                    user = User.objects.get(username=username, organization__isnull=False)
                    if user.check_password(password):
                        org_id = user.organization_id
                    else:
                        user = None
                except User.DoesNotExist:
                    pass

        else:
            # Student, Teacher, Manager, Admin
            try:
                user = User.objects.get(username=username, role=role)
                if user.check_password(password):
                    org_id = user.organization_id
                else:
                    user = None
            except User.DoesNotExist:
                pass

        if not user and not org:
            return Response({
                'success': False,
                'message': 'Invalid username or password'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Determine role
        if org:
            user_role = 'ceo'
            user_data = {
                'id': org.id,
                'name': org.ceo_name,
                'username': org.username,
                'phone': org.phone,
                'email': org.email,
                'avatar': org.avatar,
                'role': 'ceo',
            }
            if org.status != 'active':
                return Response({
                    'success': False,
                    'message': 'Organization account is inactive'
                }, status=status.HTTP_403_FORBIDDEN)
        else:
            user_role = user.role
            user_data = {
                'id': user.id,
                'name': user.name,
                'username': user.username,
                'phone': user.phone,
                'role': user.role,
                'avatar': user.avatar,
                'status': user.status,
                'group': user.group_id,
            }
            if user.status != 'active':
                return Response({
                    'success': False,
                    'message': 'User account is inactive'
                }, status=status.HTTP_403_FORBIDDEN)

        # Generate tokens
        refresh = RefreshToken()
        refresh['user_id'] = user_data['id']
        refresh['role'] = user_role
        refresh['org_id'] = org_id

        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_data,
                'org_id': org_id,
                'role': user_role,
            }
        })


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'success': False, 'message': 'Refresh token required'},
                          status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'success': True,
                'data': {
                    'access': str(refresh.access_token),
                }
            })
        except Exception as e:
            return Response({'success': False, 'message': str(e)},
                          status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        return Response({'success': True, 'message': 'Logged out successfully'})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Invalid data', 'errors': serializer.errors},
                          status=status.HTTP_400_BAD_REQUEST)

        current = serializer.validated_data['current_password']
        new = serializer.validated_data['new_password']

        user = request.user
        if not user.check_password(current):
            return Response({'success': False, 'message': 'Current password is incorrect'},
                          status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new)
        user.save()
        return Response({'success': True, 'message': 'Password changed successfully'})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'ceo':
            try:
                org = Organization.objects.get(id=user.id)
                data = {
                    'id': org.id,
                    'name': org.ceo_name,
                    'username': org.username,
                    'phone': org.phone,
                    'email': org.email,
                    'avatar': org.avatar,
                    'role': 'ceo',
                    'organization': {
                        'id': org.id,
                        'name': org.org_name,
                        'telegram_chat_id': org.telegram_chat_id,
                        'status': org.status,
                    }
                }
                return Response({'success': True, 'data': data})
            except Organization.DoesNotExist:
                pass

        serializer = UserSerializer(user)
        return Response({'success': True, 'data': serializer.data})

    def put(self, request):
        user = request.user
        if user.role == 'ceo':
            try:
                org = Organization.objects.get(id=user.id)
                serializer = OrganizationSerializer(org, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'success': True, 'message': 'Profile updated', 'data': serializer.data})
                return Response({'success': False, 'message': 'Invalid data', 'errors': serializer.errors},
                              status=status.HTTP_400_BAD_REQUEST)
            except Organization.DoesNotExist:
                pass

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Profile updated', 'data': serializer.data})
        return Response({'success': False, 'message': 'Invalid data', 'errors': serializer.errors},
                      status=status.HTTP_400_BAD_REQUEST)