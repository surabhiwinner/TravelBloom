# payment/views.py
import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from authentication.models import Traveller
from django.shortcuts import get_object_or_404,render,redirect
import razorpay 
from .models import Payments,StatusChoices,Transactions
from django.utils.timezone import now, datetime
from django.conf import settings



class PremiumConfirmationView(View):

    def get(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')

                # Fetch traveller
        traveller = get_object_or_404(Traveller, uuid=uuid)

        # Check if any successful payment exists
        payment = Payments.objects.filter(traveller=traveller, status='Success').order_by('-paid_at').first()

        if payment:
            # Optionally update traveller's premium status
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

        traveller = get_object_or_404(Traveller,uuid=uuid)

        payment =Payments.objects.get(traveller__profile = request.user)

        client = razorpay.Client(auth=(settings.config('RAZORPAY_PUBLIC_KEY'), settings.config('RAZORPAY_SECRET_KEY')))

        data = { "amount": payment.amount*100, "currency": "INR", "receipt": "order_rcptid_11" }

        transaction = Transactions.objects.create(payment=payment)

        order  = client.order.create(data=data) 

        print(order)

        rzp_order_id = order.get('id')
        transaction.rzp_order_id = rzp_order_id
        transaction.save()

        data = {
            'client_id' : settings.config('RZP_CLIENT_ID'),
            'amount'    : payment.amount*100 ,
            'rzp_order_id': rzp_order_id
        }
        return render(request, 'payments/payement-page.html', context=data)


class PaymentVerifyView(View):

    def post(self,request,*args,**kwargs):

        print(request.POST)

        rzp_order_id =request.POST.get('razorpay_order_id')

        rzp_payment_id = request.POST.get('razorpay_payment_id')

        rzp_payment_signature = request.POST.get('razorpay_signature')

        client = razorpay.Client(auth=(settings.config('RZP_CLIENT_ID'),  settings.config('RZP_CLIENT_SECRET')))

        transaction = Transactions.objects.get(rzp_order_id=rzp_order_id)

        time_now =  datetime.datetime.now()

        transaction.transaction_at = time_now

        transaction.rzp_paymenyt_id = rzp_payment_id

        transaction.rzp_payment_signature = rzp_payment_signature

        try:

            client.utility.verify_payment_signature({
                                        'razorpay_order_id': rzp_order_id,
                                        'razorpay_payment_id': rzp_payment_id,
                                        'razorpay_signature': rzp_payment_signature
                                    }) # checks the transaction is successfull or not , if not redirect to except
            
            
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

            return redirect('razorpay-view',uuid=transaction.payment.course.uuid)


@method_decorator(csrf_exempt, name='dispatch')
class UnlockAddonView(View):
    def post(self, request, *args, **kwargs):
        try:
            print("🔐 UnlockAddonView called")
            data = json.loads(request.body)
            payment_id = data.get('payment_id')
            print(f"🔍 Received Razorpay payment ID: {payment_id}")

            # Assuming user is logged in and associated with a Traveller
            traveller = Traveller.objects.get(profile=request.user)

            # Create a successful payment record
            payment = Payments.objects.create(
                traveller=traveller,
                amount=99,
                status=StatusChoices.SUCCESS,
                paid_at=now()
            )

            # Save transaction record
            Transactions.objects.create(
                payment=payment,
                rzp_paymenyt_id=payment_id,
                rzp_payment_signature="MOCK_SIGNATURE",  # Optional: replace if real
                status=StatusChoices.SUCCESS,
                transaction_at=now()
            )

            # Grant premium access
            traveller.has_premium_access = True
            traveller.save()

            return JsonResponse({"status": "success", "message": "Premium unlocked!"}, status=200)

        except Exception as e:
            print(f"❌ Error in UnlockAddonView: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
