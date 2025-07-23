from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from django.contrib.auth import authenticate
from django.db.models import Sum

from .models import User, JobOffer, WasteCollection, WorkSession, Payment

from .serializers import (
    UserRegisterSerializer,
    UserSerializer,
    JobOfferSerializer,
    WasteCollectionSerializer,
    WorkSessionSerializer,
    PaymentSerializer,

)
from .permissions import *  
from rest_framework.pagination import PageNumberPagination
from .permissions import IsCollector  


# --- Authentification & profil ---
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
    serializer_class = WasteCollectionSerializer
    permission_classes = [permissions.IsAuthenticated, IsCollector]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'collector':
            return WasteCollection.objects.filter(collector=user)
        return WasteCollection.objects.none()

    def perform_create(self, serializer):
        # Associe automatiquement le collecteur authentifié à la collecte
        serializer.save(collector=self.request.user)
    
   


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
 

        # Affiche uniquement les collectes de l'utilisateur connecté
        return WasteCollection.objects.filter(collector=self.request.user)

    def perform_create(self, serializer):
        # L'utilisateur connecté est enregistré automatiquement comme collecteur
        serializer.save(collector=self.request.user)

    def perform_update(self, serializer):
        # Empêche de changer le collecteur
        serializer.save(collector=self.request.user)

    def perform_destroy(self, instance):
        # Ne supprime que si le collecteur est bien l'auteur
        if instance.collector == self.request.user:
            instance.delete()


# --- JobOffers (publique en lecture) ---
class JobOfferViewSet(viewsets.ModelViewSet):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# --- WorkSession ---
class WorkSessionViewSet(viewsets.ModelViewSet):
    serializer_class = WorkSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsCollector]

    def get_queryset(self):
        return WorkSession.objects.filter(collector=self.request.user)

    def perform_create(self, serializer):
        serializer.save(collector=self.request.user)

# --- Paiement (lecture seule pour collecteur) ---
class PaymentListView(ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCollector]

    def get_queryset(self):
        return Payment.objects.filter(collector=self.request.user)

class CollectorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != User.Role.COLLECTOR:
            return Response({"error": "Accès non autorisé"}, status=status.HTTP_403_FORBIDDEN)

        waste_data = WasteCollection.objects.filter(collector=user)
        work_data = WorkSession.objects.filter(collector=user)
        payment_data = Payment.objects.filter(collector=user)

        response_data = {
            'stats': {
                'total_waste_kg': ((waste_data.aggregate(Sum('weight_in_grams'))['weight_in_grams__sum'] or 0) / 1000),
                'total_hours': (work_data.aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0),
                'total_earnings': (payment_data.aggregate(Sum('amount_fcfa'))['amount_fcfa__sum'] or 0),
            },
            'collections': WasteCollectionSerializer(waste_data, many=True).data,
            'work_sessions': WorkSessionSerializer(work_data, many=True).data,
            'payments': PaymentSerializer(payment_data, many=True).data
        }

        # Ajoutez les données supplémentaires si nécessaire
        if waste_data.exists():
            response_data['stats']['last_collections'] = WasteCollectionSerializer(
                waste_data.order_by('-collected_at')[:5], many=True).data
        if payment_data.exists():
            response_data['stats']['recent_payments'] = PaymentSerializer(
                payment_data.order_by('-created_at')[:3], many=True).data

        return Response(response_data)