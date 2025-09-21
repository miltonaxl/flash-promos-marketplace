from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from promotions.views import FlashPromoViewSet, ProductReservationViewSet
from stores.views import StoreViewSet, ProductViewSet
from users.views import UserViewSet

router = DefaultRouter()
router.register(r'promos', FlashPromoViewSet)
router.register(r'reservations', ProductReservationViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'products', ProductViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
]