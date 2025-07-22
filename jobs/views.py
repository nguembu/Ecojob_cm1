from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from django.contrib.auth import authenticate

from .models import User, JobOffer, WasteCollection
from .serializers import (
    UserRegisterSerializer,
    UserSerializer,
    JobOfferSerializer,
    WasteCollectionSerializer,
)
from .permissions import *  
from rest_framework.pagination import PageNumberPagination


class UserRegisterView(CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({"detail": "Email ou mot de passe incorrect"}, status=401)
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        })

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

class WasteCollectionViewSet(viewsets.ModelViewSet):
    queryset = WasteCollection.objects.all()
    serializer_class = WasteCollectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'collector':
            return WasteCollection.objects.filter(collector=user)
        return WasteCollection.objects.none()
    


# --- pagination ---
class JobOfferPagination(PageNumberPagination):
    page_size = 10


# --- JobOffers (publique en lecture) ---
class JobOfferViewSet(viewsets.ModelViewSet):
    queryset = JobOffer.objects.all().order_by('-published_at')
    serializer_class = JobOfferSerializer
    pagination_class = JobOfferPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['location', 'contract_type', 'company']
    ordering_fields = ['published_at', 'location']

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
 
