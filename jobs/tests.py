from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch
from .models import User, WasteCollection, WorkSession, Payment
from django.urls import reverse
from rest_framework.test import  APIClient
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta


class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('user-register')
        self.login_url = reverse('user-login')
        self.profile_url = reverse('user-profile')

    def create_user_and_login(self, email='ronel@example.com', password='test123'):
        user = User.objects.create_user(
            username='ronel',
            email=email,
            password=password,
            role='collector'
        )
        response = self.client.post(self.login_url, {'email': email, 'password': password})
        token = response.data['access']
        return user, token

    # 🔹 Test 1 - Inscription OK
    def test_register_valid_user(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'role': 'collector'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('access', response.data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().email, 'newuser@example.com')

    # 🔹 Test 2 - Email déjà utilisé
    def test_register_existing_email(self):
        User.objects.create_user(
            username='existing',
            email='test@example.com',
            password='pass123',
            role='collector'
        )
        data = {
            'username': 'newuser',
            'email': 'test@example.com',
            'password': 'pass123',
            'role': 'collector'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

    # 🔹 Test 3 - Login OK
    def test_login_valid_credentials(self):
        User.objects.create_user(
            username='loginuser',
            email='login@example.com',
            password='pass123',
            role='collector'
        )
        data = {'email': 'login@example.com', 'password': 'pass123'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['email'], 'login@example.com')

    # 🔹 Test 4 - Login mauvais mot de passe
    def test_login_invalid_password(self):
        User.objects.create_user(
            username='wrongpass',
            email='badpass@example.com',
            password='correctpass',
            role='collector'
        )
        data = {'email': 'badpass@example.com', 'password': 'wrongpass'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 401)
        self.assertIn('detail', response.data)

    # 🔹 Test 5 - Login utilisateur inconnu
    def test_login_unknown_email(self):
        data = {'email': 'notfound@example.com', 'password': 'any'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 401)

    # 🔹 Test 6 - Accès profil avec token
    def test_access_profile_authenticated(self):
        _, token = self.create_user_and_login()
        response = self.client.get(self.profile_url, HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'ronel@example.com')

    # 🔹 Test 7 - Accès profil sans token
    def test_access_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 401)  # 401 est correct si @permission_classes([IsAuthenticated])

    # 🔹 Test 8 - Rôle invalide
    def test_register_invalid_role(self):
        data = {
            'username': 'badrole',
            'email': 'badrole@example.com',
            'password': 'abc123',
            'role': 'admin'  # non dans Role.choices
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('role', response.data)

    # 🔹 Test 9 - Mock create_user
    @patch('jobs.serializers.User.objects.create_user')  # assure-toi que le chemin est correct
    def test_register_user_mocked(self, mock_create_user):
        mock_user = User(username='mocked', email='mocked@example.com', role='collector')
        mock_user.set_password('testpass')
        mock_user.save = lambda: None
        mock_create_user.return_value = mock_user

        data = {
            'username': 'mocked',
            'email': 'mocked@example.com',
            'password': 'testpass',
            'role': 'collector'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['email'], 'mocked@example.com')


class WasteCollectionTests(APITestCase):
    def setUp(self):
        # Création de l'utilisateur collecteur
        self.collector = User.objects.create_user(
            username='ronel',
            email='ronel@example.com',
            password='testpass123',
            role='collector'
        )

        # Connexion et récupération du token
        login = self.client.post(reverse('user-login'), {
            'email': 'ronel@example.com',
            'password': 'testpass123'
        })
        self.token = login.data['access']
        self.auth_header = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

        self.base_url = reverse('wastecollection-list')  # assure-toi que ce nom est bien dans urls.py

    # 🔹 Création d’une collecte
    def test_create_waste_collection(self):
        # Ne pas passer collector dans data; l'API doit le définir via request.user
        data = {'material': 'plastique', 'weight_in_grams': 1200}
        response = self.client.post(self.base_url, data, **self.auth_header)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['material'], 'plastique')
        # Vérifie que la collecte est bien associée au collecteur authentifié
        wc = WasteCollection.objects.get(pk=response.data['id'])
        self.assertEqual(wc.collector, self.collector)

    # 🔹 Récupération des collectes du collecteur
    def test_get_waste_collections(self):
        WasteCollection.objects.create(
            collector=self.collector, material='verre', weight_in_grams=1000
        )
        response = self.client.get(self.base_url, **self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['material'], 'verre')

    # 🔹 Modification d’une collecte
    def test_update_waste_collection(self):
        wc = WasteCollection.objects.create(
            collector=self.collector, material='papier', weight_in_grams=900
        )
        url = reverse('wastecollection-detail', kwargs={'pk': wc.pk})
        data = {'material': 'papier recyclé', 'weight_in_grams': 1100}
        response = self.client.put(url, data, **self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['material'], 'papier recyclé')

    # 🔹 Suppression d’une collecte
    def test_delete_waste_collection(self):
        wc = WasteCollection.objects.create(
            collector=self.collector, material='canettes', weight_in_grams=500
        )
        url = reverse('wastecollection-detail', kwargs={'pk': wc.pk})
        response = self.client.delete(url, **self.auth_header)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(WasteCollection.objects.count(), 0)

    # 🔹 Tentative d'accès à une collecte d'un autre utilisateur
    def test_cannot_access_other_user_waste(self):
        other_user = User.objects.create_user(
            username='john', email='john@example.com', password='pass123', role='collector'
        )
        waste = WasteCollection.objects.create(
            collector=other_user, material='fer', weight_in_grams=1500
        )
        url = reverse('wastecollection-detail', kwargs={'pk': waste.pk})

        # GET
        response = self.client.get(url, **self.auth_header)
        self.assertEqual(response.status_code, 404)  # logique : non visible

        # PUT
        response = self.client.put(url, {'material': 'aluminium', 'weight_in_grams': 1300}, **self.auth_header)
        self.assertEqual(response.status_code, 404)

        # DELETE
        response = self.client.delete(url, **self.auth_header)
        self.assertEqual(response.status_code, 404)

    # 🔹 Création sans authentification
    def test_create_waste_unauthenticated(self):
        data = {'material': 'papier', 'weight_in_grams': 500}
        response = self.client.post(self.base_url, data)
        self.assertEqual(response.status_code, 401)  # pas de token -> accès refusé


class WorkSessionTests(APITestCase):
    def setUp(self):
        # Création du collecteur
        self.collector = User.objects.create_user(
            username='ronel',
            email='ronel@example.com',
            password='testpass123',
            role='collector'
        )

        # Authentification
        response = self.client.post(reverse('user-login'), {
            'email': 'ronel@example.com',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.auth_header = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

        self.base_url = reverse('worksession-list')  # utilise le nom de route DRF

    # 🔹 Création d’une session de travail
    def test_create_work_session(self):
        data = {
            'date': '2025-07-10',
            'hours_worked': 4
        }
        response = self.client.post(self.base_url, data, **self.auth_header)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['hours_worked'], 4)
        self.assertEqual(WorkSession.objects.count(), 1)

    # 🔹 Récupération des sessions du collecteur
    def test_get_work_sessions(self):
        WorkSession.objects.create(collector=self.collector, date='2025-07-09', hours_worked=6)
        response = self.client.get(self.base_url, **self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['hours_worked'], 6)

    # 🔹 Accès non authentifié
    def test_work_session_unauthenticated(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 401)



class PaymentTests(APITestCase):

    def setUp(self):
        # Création de l'utilisateur
        self.collector = User.objects.create_user(
            username='ronel',
            email='ronel@example.com',
            password='testpass123',
            role='collector'
        )

        # Authentification
        response = self.client.post(reverse('user-login'), {
            'email': 'ronel@example.com',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.auth_header = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

        self.base_url = reverse('payment-list')  # attention à l'utilisation de reverse ici

    # 🔹 Récupération des paiements du collecteur
    def test_get_payments(self):
        Payment.objects.create(collector=self.collector, amount_fcfa=5000)
        Payment.objects.create(collector=self.collector, amount_fcfa=2500)

        response = self.client.get(self.base_url, **self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        # Validation ordonnée selon date (si ordering dans ViewSet)
        amounts = [p['amount_fcfa'] for p in response.data]
        self.assertIn(5000, amounts)
        self.assertIn(2500, amounts)

    # 🔹 Tentative sans authentification
    def test_payment_list_unauthenticated(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 401)


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