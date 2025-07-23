from rest_framework import serializers
from .models import User, JobOffer, WasteCollection, WorkSession, Payment
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Utilisateur
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

# Inscription
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# Offres d’emploi
class JobOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = '__all__'

# Collecte des déchets
class WasteCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteCollection
        fields = ['id', 'material', 'weight_in_grams', 'collected_at', 'collector']
        read_only_fields = ['collector', 'collected_at']

# Heures de travail
class WorkHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSession
        fields = '__all__'

# Paiements
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        
        
# Session de travail
class WorkSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSession
        fields = ['id', 'date', 'hours_worked', 'collector']
        read_only_fields = ['collector']
        


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = UserSerializer(self.user).data
        
        return data


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['email'] = self.user.email
        return data