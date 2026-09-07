import razorpay

from decimal import Decimal

from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import  CartItem ,Payment


# Razorpay client

client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    )
)


# CHECKOUT API

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        cart_items = CartItem.objects.filter(
            user = request.user
        )

        if not  cart_items.exists():
            return Response({
                'message' : 'Cart is empty'
            },status=400)


        total = Decimal("0")


        for item in cart_items:
            total += item.product.price * item.quantity

        return Response({
            'totalamount' : str(total),
            'currency' : 'INR'
        })


# CREATE RAZORPAY ORDER




class CreateOrderView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        cart_items = CartItem.objects.filter(
            user=request.user
        )

        if not cart_items.exists():
            return Response({
                'message' : "cart is empty"

            },status=400)

        total = Decimal("0")

        for item in cart_items:
            total += (item.product.price*item.quantity)

        amount  = int(total*100)

        order = client.order.create({
            'amount' : amount,
            'currency' : 'INR',
            'receipt' : f"user_{request.user.id}"
        })

        Payment.objects.create(
            user = request.user ,
            razorpay_order_id = order['id'],
            amount =  total


        )

        return Response({
            'key' : settings.RAZORPAY_KEY_ID,
            'order_id' : order['id'],
            'amount' : amount,
            'currency' : 'INR'


        })


# VERIFY PAYMENT



class VerifyPaymentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        payment_id = request.data.get(
            "razorpay_payment_id"
        )

        order_id = request.data.get(
            "razorpay_order_id"
        )

        signature = request.data.get(
            "razorpay_signature"
        )

        if not payment_id:

            return Response(
        {
            "message":
                "Payment ID is required"
            },
            status=400
        )

        if not order_id:

            return Response(
        {
            "message":
                "Order ID is required"
            },
            status=400
        )

        if not signature:

            return Response(
        {
            "message":
                "Signature is required"
            },
            status=400
        )

        try:

            payment = Payment.objects.get(
                razorpay_order_id=order_id,
                user=request.user
            )

        except Payment.DoesNotExist:

            return Response(
        {
            "message":
                "Payment not found"
            },
            status=404
        )

        try:

            client.utility.verify_payment_signature({

                "razorpay_order_id":
                    order_id,

                    "razorpay_payment_id":
                        payment_id,

                        "razorpay_signature":
                            signature

                        })

        except razorpay.errors.SignatureVerificationError:

            payment.status = "failed"

            payment.save()

            return Response(
        {
            "message":
                "Payment verification failed"
            },
            status=400
        )

        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.status = 'paid'
        payment.save()


        return Response({

        "message":
            "Payment successful",

            "status":
                "paid"



        })
        





