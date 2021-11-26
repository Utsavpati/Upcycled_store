from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import CustomerRegistrationForm, CustomerProfileForm
from .models import Customer, Product, Cart, order_placed,merchant
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import razorpay
from django.views.decorators.csrf import csrf_exempt, csrf_protect

def productview(request):
    topwear = Product.objects.filter(category='TW')
    laptop = Product.objects.filter(category='L')
    mobile = Product.objects.filter(category='M')
    return render(request, 'app/home.html', {'topwear': topwear, 'laptop': laptop, 'mobile': mobile})


def product_detail(request, pk):
    product = Product.objects.get(id=pk)
    item_already_in_cart=False
    if request.user.is_authenticated:
        item_already_in_cart=Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
    return render(request, 'app/productdetail.html', {'product': product,'item_already_in_cart':item_already_in_cart})

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    print(product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart')

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity*p.product.discounted_price)
                amount += tempamount
                total_amount = amount+shipping_amount
            return render(request, 'app/addtocart.html', {'carts': cart, 'total_amount': total_amount, 'amount': amount})
        else:
            return render(request, 'app/emptycart.html')


def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        for p in cart_product:
            tempamount = (p.quantity*p.product.discounted_price)
            amount += tempamount
            totalamount = amount+shipping_amount

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)

def minus_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        for p in cart_product:
            tempamount = (p.quantity*p.product.discounted_price)
            amount += tempamount
            

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount' : amount+shipping_amount
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        for p in cart_product:
            tempamount = (p.quantity*p.product.discounted_price)
            amount += tempamount
            

        data = {
            'amount': amount,
            'totalamount' : amount+shipping_amount
        }
        return JsonResponse(data)

def buy_now(request):
    return render(request, 'app/buynow.html')

@login_required
def payment_done(request):
    user=request.user
    custid=request.GET.get('custid')
    customer=Customer.objects.get(id=custid)
    cart=Cart.objects.filter(user=user)
    for c in cart:
        order_placed(user=user,customer=customer,product=c.product,quantity=c.quantity).save()
        c.delete()
    return redirect("orders")

@login_required
def profile(request):
    if request.method == 'GET':
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})

    if request.method == 'POST':
        print("asdfg")
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations Profile has been added")
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            zipcode = form.cleaned_data['zipcode']
            state = form.cleaned_data['state']
            reg = Customer(user=user, name=name, locality=locality,
                           city=city, state=state, zipcode=zipcode)
            reg.save()
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})

@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add': add, 'active': 'btn-primary'})

@login_required
def orders(request):
    op=order_placed.objects.filter(user=request.user)
    return render(request, 'app/orders.html',{'order_placed':op})


def mobile(request, data=None):
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'Redmi' or data == 'Samsung':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'below':
        mobiles = Product.objects.filter(
            category='M').filter(discounted_price__lt=10000)
    elif data == 'above':
        mobiles = Product.objects.filter(
            category='M').filter(discounted_price__gt=10000)
    return render(request, 'app/mobile.html', {'mobiles': mobiles})


def login(request):
    return render(request, 'app/login.html')


def customerregistration(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations you have been added")
            form.save()
        return render(request, 'app/customerregistration.html', {'form': form})
    else:
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

@login_required
def checkout(request):
    client = razorpay.Client(auth=("Key Id", "Key Secret"))
    user=request.user
    add=Customer.objects.filter(user=user)
    cart_items=Cart.objects.filter(user=user)
    amount=0.0
    shipping_cart=70
    totalamount=0
    cart_product=[p for p in Cart.objects.all() if p.user==request.user]

    if cart_product:
        for p in cart_product:
            tempamount=(p.quantity*p.product.discounted_price)
            amount+=tempamount
        totalamount_INR=int(amount+shipping_cart)*100
        totalamount=amount+shipping_cart
        print(totalamount,totalamount_INR)
    DATA = {
        "amount": totalamount_INR,
        "currency": "INR",
        "receipt": "receipt#1",
        "notes": {
            "key1": "value3",
            "key2": "value2"
        }
    }
    order=client.order.create(data=DATA)
    print(order,totalamount_INR)
    return render(request, 'app/checkout.html',{'add':add,'totalamount':totalamount,'totalamount_INR':totalamount_INR,'cart_items':cart_items,'order_id':order['id']})


@login_required
def sellwithus(request):
    if request.method=='POST':
        first=request.user.first_name
        last=request.user.last_name
        email=request.user.email
        address=request.POST['address']        
        merch=request.user
        m= merchant(first=first,last=last,email=email, address= address,merch=merch)
        m.save()
    else:
        first=request.user.first_name
        last=request.user.last_name
        email=request.user.email     
        merch=request.user
        return render(request,'app/sellwithus.html',{'first':first,'last':last,'email':email})


@csrf_exempt
def paysuccess(request):
    
    customer=Customer.objects.get(id=request.user.id)
    cart=Cart.objects.filter(user=request.user)
    for c in cart:
        order_placed(user=request.user,customer=customer,product=c.product,quantity=c.quantity).save()
        c.delete()
    return render(request,'app/paysuccess.html')