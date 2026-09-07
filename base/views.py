from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Product, CartItem 
from .serializers.registerserializer import RegisterSerializer
from .serializers.productserializer import ProductSerializer
from .serializers.cartserializer import CartItemSerializer

from .permissions import IsStaffUser
from .pagination import ProductPagination
from .throttles import ProductCreateThrottle









# =========================
# REGISTER API
# =========================

class RegisterView(generics.CreateAPIView):

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


    # =========================
    # LOGIN API
    # =========================

class LoginView(TokenObtainPairView):

    permission_classes = [AllowAny]


    # =========================
    # PRODUCT APIs
    # =========================

class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_fields = [
        "price",
        "stock"
    ]

    search_fields = [
        "name",
        "description"
    ]

    ordering_fields = [
        "price",
        "created_at"
    ]

    throttle_classes = [
        ProductCreateThrottle
    ]

    def get_permissions(self):

        if self.action in ["list", "retrieve"]:

            return [
        IsAuthenticated()
    ]

        return [
        IsAuthenticated(),
        IsStaffUser()
    ]


    # Cart Apis 
class CartViewSet(viewsets.ModelViewSet):

    serializer_class = CartItemSerializer
    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return CartItem.objects.filter(
    user=self.request.user
)

    def perform_create(self, serializer):

        serializer.save(
            user=self.request.user
        )
