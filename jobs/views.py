from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, JobOffer, WasteCollection
from .serializers import (
    UserRegisterSerializer,
    UserSerializer,
    EmailTokenObtainPairSerializer,
    JobOfferSerializer,
    WasteCollectionSerializer
)

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .models import  WorkSession, Payment
from .serializers import ( 
    WorkSessionSerializer,
    PaymentSerializer
)


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

class JobOfferViewSet(viewsets.ModelViewSet):

    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


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