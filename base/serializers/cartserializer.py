from rest_framework import serializers
from ..models import CartItem


class CartItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    product_price = serializers.DecimalField(
        source="product.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    product_image = serializers.SerializerMethodField()

    product_stock = serializers.IntegerField(
        source="product.stock",
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_price",
            "product_image",
            "product_stock",
            "quantity",
        ]

    def get_product_image(self, obj):
        """Return the full Cloudinary URL or None."""
        if not obj.product.image:
            return None
        try:
            return obj.product.image.url
        except Exception:
            return None
