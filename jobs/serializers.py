from rest_framework import serializers
from .models import User, JobOffer, WasteCollection, WorkHour, Payment

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
        fields = '__all__'

# Heures de travail
class WorkHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkHour
        fields = '__all__'

# Paiements
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
