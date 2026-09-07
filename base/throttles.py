from rest_framework.throttling import UserRateThrottle

class ProductCreateThrottle(UserRateThrottle):
    scope = "product_create"