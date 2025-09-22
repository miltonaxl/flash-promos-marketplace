from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from promotions.views import FlashPromoViewSet, ProductReservationViewSet
from stores.views import StoreViewSet, ProductViewSet
from users.views import UserViewSet
from notifications.views import NotificationViewSet

router = DefaultRouter()
router.register(r'flash-promos', FlashPromoViewSet, basename='flashpromo')
router.register(r'product-reservations', ProductReservationViewSet, basename='productreservation')
router.register(r'stores', StoreViewSet)
router.register(r'products', ProductViewSet)
router.register(r'users', UserViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('admin/', admin.site.urls),
    # JWT Token endpoints (legacy)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Custom auth endpoints
    path('api/auth/login/', UserViewSet.as_view({'post': 'login'}), name='auth_login'),
    path('api/users/register/', UserViewSet.as_view({'post': 'register'}), name='user_register'),
    path('api/users/profile/', UserViewSet.as_view({'get': 'profile'}), name='user_profile'),
    # API routes
    path('api/', include(router.urls)),
]