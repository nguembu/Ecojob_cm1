from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User, JobOffer, WasteCollection, WorkSession, Payment
from .serializers import (
    UserRegisterSerializer,
    UserSerializer,
    JobOfferSerializer,
    WasteCollectionSerializer,
    WorkSessionSerializer,
    PaymentSerializer
)
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

