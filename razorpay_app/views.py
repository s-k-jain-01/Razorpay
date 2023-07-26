from django.shortcuts import render,redirect
import razorpay
from django.conf import settings
from rest_framework.decorators import api_view
from django.http import HttpResponse
from .models import Product
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
client = razorpay.Client(auth=(settings.RAZORPAY_CLIENT_ID,settings.RAZORPAY_CLIENT_SECRET))

def home(request):
    products=Product.objects.all()
    return render(request,'index.html',{'products':products})

@api_view(['POST'])
def create_order(request):
    amount=int(request.POST['amount'])*100
    quantity=int(request.POST['quantity'])
    amount*=quantity
    response=client.order.create({
        "amount": amount,
        "currency": "INR"
    })
    return render(request,'payment.html',{'response':response,'key':settings.RAZORPAY_CLIENT_ID})    

@api_view(['GET'])
def order_details(request):
    respone=client.order.all()          #.fetch() for specific order_id
    return HttpResponse(json.dumps(respone))

@csrf_exempt
def capture_payment(request):
    payment_id=request.POST['razorpay_payment_id']
    response=client.payment.fetch(payment_id)
    return render(request,'pay_info.html',{'response':response})

def refund(request):
    paymentId=request.POST['paymentId']
    amount=request.POST['amount']
    response=client.payment.refund(paymentId,{
        "amount": amount,
        "speed": "normal"
    })
    refund_id=response['id']
    payment_id=response['payment_id']
    return redirect(f'/refund_details/?refund_id={refund_id}&payment_id={payment_id}')

def refund_details(request):
    refundId=request.GET['refund_id']
    paymentId=request.GET['payment_id']
    response=client.payment.fetch_refund_id(paymentId,refundId)
    return render(request,'refund_data.html',{'response':response})