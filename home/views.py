from django.shortcuts import render,  HttpResponse, redirect
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# to activate the user account
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import NoReverseMatch, reverse
from django.template.loader import render_to_string

# emails
from email.message import EmailMessage
from django.core.mail import send_mail
from django.core.mail import BadHeaderError
from django.core import mail
from django.conf import settings
import threading
from threading import Thread
from django.views import View

from django.core.exceptions import ObjectDoesNotExist
import stripe
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.shortcuts import render, get_list_or_404, redirect, get_object_or_404


# Create your views here.
class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message=email_message
    def run(self):
        self.email_message.send()

def header(request):
    return render(request, 'header.html')

def footer(request):
    return render(request, 'footer.html')

def index(request):
    products = Product.objects.all()

    if request.method == 'POST':
        prd = request.POST.get('cart_id')
        print(prd)
    

    return render(request, 'index.html', {'products': products})

def signup(request):
    if(request.method == 'POST'):
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        if pass1!=pass2:
            messages.info(request, 'Password is not Matching')
            return redirect('signup')
        
        try:
            if User.objects.get(email=email):
                messages.warning(request, 'Email has been already taken')
                return redirect('signup')
        except Exception:
            pass

        user = User.objects.create_user(username = email, password=pass1, first_name=fname)
        user.save()
       
        send_mail(
            'Testing Mail',
            'Here is the message.',
            'stlonline0@gmail.com',
            [email],
            fail_silently=False,
            )
        # new_user = authenticate(username=form.cleaned_data['username'],
        #                             password=form.cleaned_data['password1'],
        #                             )
        
        # messages.info(request, "Signup SuccessFul! Please Login ") 
        login(request, user)
        messages.success(request, 'Login Success!!')
        return redirect('index')
        
    return render(request, 'signup.html')

def signin(request):
    if(request.method == 'POST'):
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')

        user = authenticate(username= email, password= pass1)
    
        if user:
            login(request, user)
            messages.success(request, 'Login Success!!')
            return render(request, 'index.html')
            # qs = SignUp.objects.filter(email=email)
            # info = {'query_set': qs}
            # if qs:
            #     return render(request, 'index.html', context=info)
            # return render(request, 'index.html')
        else:
            return render(request, 'signin.html')

    return render(request, 'signin.html')

def logout_view(request):
    logout(request)
    return redirect('/signin')

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
        cart.save()
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < cart_item.product.product_stock:
            cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart
        )
        cart_item.save()

    return redirect('cart_detail')

def cart_detail(request, total=0, counter=0, cart_items = None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.product_price * cart_item.quantity)
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_total = int(total * 100)
    description = 'XYZ-Store - New Order'
    data_key = settings.STRIPE_PUBLISHABLE_KEY

    if request.method == 'POST':
        try:
            token = request.POST['stripeToken']
            email = request.POST['stripeEmail']
            billingName = request.POST['stripeBillingName']
            billingAddress1 = request.POST['stripeBillingAddressLine1']
            billingCity = request.POST['stripeBillingAddressCity']
            billingPostcode = request.POST['stripeBillingAddressZip']
            billingCountry = request.POST['stripeBillingAddressCountryCode']
            shippingName = request.POST['stripeShippingName']
            shippingAddress1 = request.POST['stripeShippingAddressLine1']
            shippingCity = request.POST['stripeShippingAddressCity']
            shippingPostcode = request.POST['stripeShippingAddressZip']
            shippingCountry = request.POST['stripeShippingAddressCountryCode']
            customer = stripe.Customer.create(
                email = email,
                source = token
            )
            charge = stripe.Charge.create(
                amount = stripe_total,
                currency = 'inr',
                description = description,
                customer = customer.id
            )

            # Creating the order
            try: 
                order_details = Order.objects.create(
                                token = token,
                                total = total,
                                emailAddress = email,
                                billingName = billingName,
                                billingAddress1 = billingAddress1,
                                billingCity = billingCity,
                                billingPostcode = billingPostcode,
                                billingCountry = billingCountry,
                                shippingName = shippingName,
                                shippingAddress1 = shippingAddress1,
                                shippingCity = shippingCity,
                                shippingPostcode = shippingPostcode,
                                shippingCountry = shippingCountry
                )
                order_details.save()
                for order_item in cart_items:
                    or_item = OrderItem.objects.create(
                        product = order_item.product.product_name,
                        quantity = order_item.quantity,
                        price = order_item.product.product_price,
                        order = order_details
                    )
                    or_item.save()

                    # Reduce Stock
                    products = Product.objects.get(id=order_item.product.id)
                    products.product_stock = int(order_item.product.product_stock - order_item.quantity)
                    products.save()
                    order_item.delete()

                    # Print a message when the order is created
                    print('The order has been Created')
                    
                try:
                    send_mail(order_details.id)
                    print('The order email has been sent')
                except IOError as e:
                    return e

                return redirect('thanks_page', order_details.id)
            except ObjectDoesNotExist:
                pass     

        except stripe.error.CardError as e:
            return False, e

    return render(request, 'cart.html', dict(cart_items = cart_items, total = total, counter = counter, data_key = data_key, stripe_total = stripe_total, description = description))

def cart_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_detail')

def cart_remove_product(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart_detail')
