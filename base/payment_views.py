import razorpay

from decimal import Decimal

from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import CartItem, Payment


# ============================================================
# Lazily create the Razorpay client so it reads settings AFTER
# Django has fully initialised them (avoids None key at import time).
# ============================================================

def get_razorpay_client():
    return razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )
    )


# ============================================================
# CHECKOUT  GET /api/checkout/
# Returns cart total so the frontend can preview before paying
# ============================================================

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = CartItem.objects.filter(
            user=request.user
        ).select_related("product")

        if not cart_items.exists():
            return Response({"message": "Cart is empty"}, status=400)

        total = Decimal("0")
        items = []
        for item in cart_items:
            subtotal = item.product.price * item.quantity
            total += subtotal
            items.append({
                "product_id":   item.product.id,
                "product_name": item.product.name,
                "unit_price":   str(item.product.price),
                "quantity":     item.quantity,
                "subtotal":     str(subtotal),
            })

        return Response({
            "items":        items,
            "total_amount": str(total),
            "currency":     "INR",
        })


# ============================================================
# CREATE RAZORPAY ORDER  POST /api/create-order/
# ============================================================

class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart_items = CartItem.objects.filter(
            user=request.user
        ).select_related("product")

        if not cart_items.exists():
            return Response({"message": "Cart is empty"}, status=400)

        total = Decimal("0")
        for item in cart_items:
            total += item.product.price * item.quantity

        # Razorpay expects amount in paise (smallest INR unit)
        amount_paise = int(total * 100)

        try:
            client = get_razorpay_client()
            order = client.order.create({
                "amount":   amount_paise,
                "currency": "INR",
                "receipt":  f"user_{request.user.id}",
            })
        except razorpay.errors.BadRequestError as e:
            return Response(
                {"message": f"Razorpay error: {str(e)}"},
                status=502
            )
        except Exception as e:
            return Response(
                {"message": "Failed to create payment order. Please try again."},
                status=500
            )

        Payment.objects.create(
            user=request.user,
            razorpay_order_id=order["id"],
            amount=total,
        )

        return Response({
            "key":      settings.RAZORPAY_KEY_ID,
            "order_id": order["id"],
            "amount":   amount_paise,
            "currency": "INR",
        })


# ============================================================
# VERIFY PAYMENT  POST /api/verify-payment/
# ============================================================

class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_id = request.data.get("razorpay_payment_id")
        order_id   = request.data.get("razorpay_order_id")
        signature  = request.data.get("razorpay_signature")

        # Validate all three fields are present
        for field, value in [
            ("razorpay_payment_id", payment_id),
            ("razorpay_order_id",   order_id),
            ("razorpay_signature",  signature),
        ]:
            if not value:
                return Response(
                    {"message": f"{field} is required"},
                    status=400
                )

        # Fetch our payment record
        try:
            payment = Payment.objects.get(
                razorpay_order_id=order_id,
                user=request.user,
            )
        except Payment.DoesNotExist:
            return Response({"message": "Payment record not found"}, status=404)

        # Guard against replaying an already-processed payment
        if payment.status == "paid":
            return Response({"message": "Payment already verified", "status": "paid"})

        # Verify signature with Razorpay
        try:
            client = get_razorpay_client()
            client.utility.verify_payment_signature({
                "razorpay_order_id":   order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature":  signature,
            })
        except razorpay.errors.SignatureVerificationError:
            payment.status = "failed"
            payment.save()
            return Response(
                {"message": "Signature verification failed. Payment is invalid."},
                status=400
            )

        # Mark payment as paid
        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature  = signature
        payment.status = "paid"
        payment.save()

        # Clear the user's cart after successful payment
        CartItem.objects.filter(user=request.user).delete()

        return Response({
            "message": "Payment successful",
            "status":  "paid",
        })
