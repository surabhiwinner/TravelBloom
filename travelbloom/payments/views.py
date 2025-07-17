import json
import razorpay
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
        payment = Payments.objects.get(traveller__profile=request.user)

        client = razorpay.Client(auth=(settings.config('RAZORPAY_PUBLIC_KEY'), settings.config('RAZORPAY_SECRET_KEY')))
        data = {"amount": int(payment.amount * 100), "currency": "INR", "receipt": "order_rcptid_11"}

        transaction = Transactions.objects.create(payment=payment)
        order = client.order.create(data=data)

        transaction.rzp_order_id = order.get('id')
        transaction.save()

        context = {
            'client_id': settings.config('RZP_CLIENT_ID'),
            'amount': int(payment.amount * 100),
            'rzp_order_id': order.get('id')
        }
        return render(request, 'payments/payement-page.html', context=context)


class PaymentVerifyView(View):
    def post(self, request, *args, **kwargs):
        rzp_order_id = request.POST.get('razorpay_order_id')
        rzp_payment_id = request.POST.get('razorpay_payment_id')
        rzp_payment_signature = request.POST.get('razorpay_signature')

        client = razorpay.Client(auth=(settings.config('RZP_CLIENT_ID'), settings.config('RZP_CLIENT_SECRET')))
        transaction = Transactions.objects.get(rzp_order_id=rzp_order_id)
        time_now = datetime.datetime.now()

        transaction.transaction_at = time_now
        transaction.rzp_payment_id = rzp_payment_id
        transaction.rzp_payment_signature = rzp_payment_signature

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': rzp_order_id,
                'razorpay_payment_id': rzp_payment_id,
                'razorpay_signature': rzp_payment_signature
            })

            transaction.status = 'Success'
            transaction.save()

            transaction.payment.status = 'Success'
            transaction.payment.paid_at = time_now
            transaction.payment.save()

            return redirect('home')
        except:
            transaction.status = 'Failed'
            transaction.save()

            transaction.payment.status = 'Failed'
            transaction.payment.save()

            return redirect('razorpay-view', uuid=transaction.payment.course.uuid)


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
