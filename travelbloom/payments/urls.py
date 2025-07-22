# payment/urls.py
from django.urls import path
from . import views

urlpatterns = [

    path('confirm/<str:uuid>/', views.PremiumConfirmationView.as_view(), name='premium-confirmation'),
    path('razorpay/<str:uuid>/', views.RazorpayView.as_view(), name='razorpay-page'),
    path('verify/', views.PaymentVerifyView.as_view(), name='verify-payment'),  # ✅ ADD THIS LINE
    path('unlock/', views.UnlockAddonView.as_view(), name='unlock_addon'),
]
