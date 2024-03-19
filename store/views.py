from django.shortcuts import render

from .models import *

from django.http import JsonResponse

import json

import datetime

from .forms import CreateUserForm

# Create your views here.

def landingpage(request):
    contxt = {}
    return render(request, 'store/landingpage.html', contxt)
def about(request):
    contxt = {}
    return render(request, 'store/about.html', contxt)

def registerPage(request):
    form = CreateUserForm()
    
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
    contxt = {'form': form}
    return render(request, 'store/register.html', contxt)

def loginPage(request):
    contxt = {}
    return render(request, 'store/login.html', contxt)

def cart(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = []
        print(cart)
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order.get_cart_items

    contxt = {'items': items, 'order': order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', contxt)


def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

    products = Product.objects.all()
    contxt = {'products': products, 'cartItems':cartItems}
    return render(request, 'store/store.html', contxt)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

    contxt = {'items': items, 'order': order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', contxt)

def updateItem(request):
    
    data = json.loads(request.body)

    productId = data['productId']

    action = data['action']

    print('Action:', action)

    print('Product:', productId)
    
    customer = request.user.customer

    product = Product.objects.get(id=productId)

    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    
    return JsonResponse('An item has been added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()
        
        if order.shipping == True:
            ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            )

    else:
        print('User is not logged in')
    
    return JsonResponse('Payment has being submitted..', safe=False)