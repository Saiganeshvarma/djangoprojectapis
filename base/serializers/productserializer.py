from rest_framework import serializers
from ..models import Product


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"

    def to_representation(self, instance):
        """
        Override output only.
        Cloudinary's default serialization returns just the partial path
        (e.g. 'image/upload/v.../filename.jpg').
        We replace it with the full HTTPS URL so the frontend can use it directly.
        """
        data = super().to_representation(instance)

        if instance.image:
            try:
                data["image"] = instance.image.url
            except Exception:
                data["image"] = None
        else:
            data["image"] = None

        return data

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than zero."
            )
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Stock cannot be negative."
            )
        return value
