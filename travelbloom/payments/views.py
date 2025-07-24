import json
import razorpay
from datetime import datetime
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.timezone import now, datetime
from django.conf import settings
from authentication.models import Traveller
from .models import Payments, StatusChoices, Transactions


class PremiumConfirmationView(View):
    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        traveller = get_object_or_404(Traveller, uuid=uuid)

        payment = Payments.objects.filter(traveller=traveller, status='Success').order_by('-paid_at').first()

        if payment:
            traveller.has_premium_access = True
            traveller.save()
            message = "Premium access granted"
        else:
            message = "No successful payment found"

        context = {
            'traveller': traveller,
            'payment': payment,
            'message': message
        }
        return render(request, 'payments/premium-confirmation.html', context)


class RazorpayView(View):
    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        traveller = get_object_or_404(Traveller, uuid=uuid)

        # Check if payment exists or create one
        payment = Payments.objects.filter(traveller=traveller).first()
        if not payment:
            payment = Payments.objects.create(traveller=traveller, amount=99)

        # Razorpay client
        client = razorpay.Client(auth=(
            settings.RAZORPAY_PUBLIC_KEY,
            settings.RAZORPAY_SECRET_KEY
        ))

        # Create Razorpay order
        order_data = {
            "amount": int(payment.amount * 100),  # Amount in paise
            "currency": "INR",
            "receipt": f"receipt_{payment.pk}"
        }

         # Create transaction and order
        transaction = Transactions.objects.create(payment=payment)
        razorpay_order = client.order.create(data=order_data)

        # Save order_id to transaction
        transaction.rzp_order_id = razorpay_order.get('id')
        transaction.save()

        # Send necessary context to template
        context = {
            'client_id': settings.RAZORPAY_PUBLIC_KEY,
            'amount': order_data["amount"],
            'rzp_order_id': razorpay_order.get('id'),
            'traveller': traveller,
            'return_url': request.GET.get('next', '/'),  # Pass manually or fallback

        }

        return render(request, 'payments/payment-page.html', context=context)


class PaymentVerifyView(View):
    def post(self, request, *args, **kwargs):
        rzp_order_id = request.POST.get('razorpay_order_id')
        rzp_payment_id = request.POST.get('razorpay_payment_id')
        rzp_payment_signature = request.POST.get('razorpay_signature')

        client = razorpay.Client(auth=(settings.RAZORPAY_PUBLIC_KEY, settings.RAZORPAY_SECRET_KEY))
        transaction = Transactions.objects.get(rzp_order_id=rzp_order_id)
        time_now = datetime.now()

        transaction.transaction_at = time_now
        transaction.rzp_payment_id = rzp_payment_id
        transaction.rzp_payment_signature = rzp_payment_signature

        try:
            # Razorpay signature verification
            client.utility.verify_payment_signature({
                'razorpay_order_id': rzp_order_id,
                'razorpay_payment_id': rzp_payment_id,
                'razorpay_signature': rzp_payment_signature
            })

            # Mark transaction and payment as successful
            transaction.status = 'Success'
            transaction.save()

            payment = transaction.payment
            payment.status = 'Success'
            payment.paid_at = time_now
            payment.save()

            # Grant premium access
            traveller = payment.traveller
            traveller.profile.has_premium_access = True
            traveller.profile.save()

            return redirect('home')  # Redirect to previous page or home
        except Exception as e:
            transaction.status = 'Failed'
            transaction.save()

            transaction.payment.status = 'Failed'
            transaction.payment.save()

            return redirect('home')  # Redirect back on failure


@method_decorator(csrf_exempt, name='dispatch')
class UnlockAddonView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            payment_id = data.get('payment_id')
            traveller = Traveller.objects.get(profile=request.user)

            # Create successful payment record
            payment = Payments.objects.create(
                traveller=traveller,
                amount=99,
                status=StatusChoices.SUCCESS,
                paid_at=now()
            )

            # Save transaction
            Transactions.objects.create(
                payment=payment,
                rzp_payment_id=payment_id,
                rzp_payment_signature="MOCK_SIGNATURE",
                status=StatusChoices.SUCCESS,
                transaction_at=now()
            )

            # Grant premium access
            traveller.has_premium_access = True
            traveller.save()

            return JsonResponse({"status": "success", "message": "Premium unlocked!"}, status=200)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
