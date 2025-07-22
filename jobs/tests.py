from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from jobs.models import WasteCollection, WorkSession, Payment
from datetime import datetime, timedelta

User = get_user_model()
class CollectorDashboardViewTests(APITestCase):
    def setUp(self):
        self.collector = User.objects.create_user(
            username='collector',
            email='collector@example.com',
            password='pass',
            role=User.Role.COLLECTOR
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='pass',
            role='admin'
        )
        self.client = APIClient()
        self.url = '/api/collector-dashboard/'  

    def test_access_denied_for_non_collector(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_granted_for_collector(self):
        self.client.force_authenticate(user=self.collector)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_total_waste_kg_calculation(self):
        WasteCollection.objects.create(
            collector=self.collector, 
            weight_in_grams=5000, 
            collected_at=datetime.now()
        )
        WasteCollection.objects.create(
            collector=self.collector, 
            weight_in_grams=3000, 
            collected_at=datetime.now()
        )
        self.client.force_authenticate(user=self.collector)
        response = self.client.get(self.url)
        self.assertEqual(response.data['stats']['total_waste_kg'], 8.0)  # (5000 + 3000)/1000

    def test_total_hours_calculation(self):
        WorkSession.objects.create(
            collector=self.collector,
            date=datetime.now().date(),  
            hours_worked=2
        )
        WorkSession.objects.create(
            collector=self.collector,
            date=datetime.now().date(),  
            hours_worked=3
        )
        self.client.force_authenticate(user=self.collector)
        response = self.client.get(self.url)
        self.assertEqual(response.data['stats']['total_hours'], 5)

    def test_total_earnings_calculation(self):
        Payment.objects.create(collector=self.collector, amount_fcfa=1000)
        Payment.objects.create(collector=self.collector, amount_fcfa=2000)
        self.client.force_authenticate(user=self.collector)
        response = self.client.get(self.url)
        self.assertEqual(response.data['stats']['total_earnings'], 3000)

    def test_last_collections_limit(self):
        for i in range(7):
            WasteCollection.objects.create(collector=self.collector, weight_in_grams=1000, collected_at=datetime.now() - timedelta(days=i))
        self.client.force_authenticate(user=self.collector)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['stats']['last_collections']), 5)

    def test_recent_payments_limit(self):
        for i in range(5):
            Payment.objects.create(collector=self.collector, amount_fcfa=1000, created_at=datetime.now() - timedelta(days=i))
        self.client.force_authenticate(user=self.collector)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['stats']['recent_payments']), 3)

    def test_collections_serializer(self):
        WasteCollection.objects.create(collector=self.collector, weight_in_grams=1000, collected_at=datetime.now())
        self.client.force_authenticate(user=self.collector)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['collections']), 1)

    def test_work_sessions_serializer(self):
        WorkSession.objects.create(
            collector=self.collector,
            hours_worked=2,
            date=datetime.now().date()  
        )
        self.client.force_authenticate(user=self.collector)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['work_sessions']), 1)

    def test_payments_serializer(self):
        Payment.objects.create(collector=self.collector, amount_fcfa=1000)
        self.client.force_authenticate(user=self.collector)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['payments']), 1)