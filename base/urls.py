from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegisterView, LoginView, ProductViewSet ,CartViewSet

from .payment_views import CheckoutView,CreateOrderView,VerifyPaymentView
router = DefaultRouter()


router.register(
    "products",
    ProductViewSet,
    basename="products"
)

router.register(
    "cart",
    CartViewSet,
    basename="cart"
)


urlpatterns = [
    path(
        "register/",
        RegisterView.as_view(),
        name="register"
    ),

    path(
        "login/",
        LoginView.as_view(),
        name="login"
    ),

    path(
        "",
        include(router.urls)
    ),
    
    path(
    "checkout/",
    CheckoutView.as_view(),
    name="checkout"
),

path(
    "create-order/",
    CreateOrderView.as_view(),
    name="create-order"
),

path(
    "verify-payment/",
    VerifyPaymentView.as_view(),
    name="verify-payment"
)
]