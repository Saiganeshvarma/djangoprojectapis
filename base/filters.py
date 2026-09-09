import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Supports all filter params the frontend uses:

    ?search=keyword          → searches name + description (via SearchFilter)
    ?price_min=100           → price >= 100
    ?price_max=999           → price <= 999
    ?stock_min=1             → stock >= 1  (stock_min=1 means "in stock only")
    ?ordering=price          → cheapest first
    ?ordering=-price         → most expensive first
    ?ordering=created_at     → oldest first
    ?ordering=-created_at    → newest first (default)
    """

    price_min = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
        label="Min price"
    )

    price_max = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
        label="Max price"
    )

    stock_min = django_filters.NumberFilter(
        field_name="stock",
        lookup_expr="gte",
        label="Min stock"
    )

    class Meta:
        model = Product
        fields = ["price_min", "price_max", "stock_min"]
