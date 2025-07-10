from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserRegisterView,
    UserLoginView,
    UserProfileView,
    WasteCollectionViewSet,
    JobOfferViewSet,
    WorkSessionViewSet,
    PaymentListView
)

router = DefaultRouter()
router.register(r'waste-collections', WasteCollectionViewSet, basename='wastecollection')
router.register(r'job-offers', JobOfferViewSet, basename='joboffer')
router.register(r'work-sessions', WorkSessionViewSet, basename='worksession')

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('', include(router.urls)),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
]
