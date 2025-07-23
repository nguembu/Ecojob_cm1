from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        COLLECTOR = 'collector', _('Collecteur')
        RECRUITER = 'recruiter', _('Recruteur')
        BUYER = 'buyer', _('Acheteur')

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class JobOffer(models.Model):
    CONTRACT_CHOICES = [
        ('CDI', 'CDI'),
        ('CDD', 'CDD'),
        ('Stage', 'Stage'),
        ('Freelance', 'Freelance'),
    ]

    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField()
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    contract_type = models.CharField(max_length=50, choices=CONTRACT_CHOICES)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
  

class WasteCollection(models.Model):
    collector = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'collector'})
    material = models.CharField(max_length=100)
    weight_in_grams = models.PositiveIntegerField()
    collected_at = models.DateTimeField(auto_now_add=True)

    @property
    def weight_in_kg(self):
        return self.weight_in_grams / 1000

    def __str__(self):
        return f"{self.material} - {self.weight_in_kg} kg"

class WorkSession(models.Model):
    collector = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'collector'})
    date = models.DateField()
    hours_worked = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.collector.username} - {self.date}"

class Payment(models.Model):
    collector = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'collector'})
    amount_fcfa = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.collector.username} - {self.amount_fcfa} FCFA"
