from django.shortcuts import render,redirect
from django.views import View
from .models import Customer,Product,Cart,OrderPlaced
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import  Q
from django.http import JsonResponse
from  django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# def home(request):
#  return render(request, 'app/home.html')
class ProductView(View):
    def get(self,request):
        topwears=Product.objects.filter(category='TW')
        bottomwears=Product.objects.filter(category='BW')
        mobile=Product.objects.filter(category='M')
        context={'topwears':topwears,'bottomwears':bottomwears,'mobile':mobile}
        return render(request,'app/home.html',context)
        
        


# def product_detail(request):
#  return render(request, 'app/productdetail.html')

# we have to make this view as a class based view because we also need to get its id
class ProductDetailView(View):
    def get(self,request,pk):
        product=Product.objects.get(pk=pk)
        item_in_cart=False
        if request.user.is_authenticated:
            item_in_cart=Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        context={'product':product,'item_in_cart':item_in_cart}
        return render(request,'app/productdetail.html',context)
    
@login_required
def add_to_cart(request):
 user=request.user
 product_id=request.GET.get('prod_id')
 product=Product.objects.get(id=product_id)
 Cart(user=user,product=product).save()
 return redirect('/cart')

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user=request.user
        cart=Cart.objects.filter(user=user)
        amount=0.0
        totalamount=0.0
        shippingamount=50
        
        cart_product=[p for p in Cart.objects.all() if p.user==user]
        
        if cart_product:
            for p in cart_product:
                temp_amount=(p.quantity*p.product.discounted_price)
                amount+=temp_amount
                totalamount=amount+shippingamount
            return render(request,'app/addtocart.html',{'carts':cart,'amount':amount,'totalamount':totalamount})
        else:
            return render(request,'app/emptycart.html')
    
   
def buy_now(request):
 return render(request, 'app/buynow.html')


@login_required
def address(request):
    add=Customer.objects.filter(user=request.user)
    return render(request,'app/address.html',{'add':add,'active':'btn-primary'})

def orders(request):
    op=OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html',{'order_placed':op})

def plus_cart(request):
    if request.method=='GET':
        prod_id=request.GET['prod_id']
        print(prod_id)
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        amount=0.0
        shippingamount=70.0
        cart_product=[p for p in Cart.objects.all() if p.user==request.user]
        for p in cart_product:
            temp_amount=(p.quantity*p.product.discounted_price)
            amount+=temp_amount
        
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':amount+shippingamount
        }
        return JsonResponse(data)
    
def minus_cart(request):
    if request.method=='GET':
        prod_id=request.GET['prod_id']
        print(prod_id)
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        amount=0.0
        shippingamount=70.0
        cart_product=[p for p in Cart.objects.all() if p.user==request.user]
        for p in cart_product:
            temp_amount=(p.quantity*p.product.discounted_price)
            amount+=temp_amount
        
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':amount+shippingamount
        }
        return JsonResponse(data)
         
  
def remove_cart(request):
    if request.method=='GET':
        prod_id=request.GET['prod_id']
        print(prod_id)
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount=0.0
        shippingamount=70.0
        cart_product=[p for p in Cart.objects.all() if p.user==request.user]
        for p in cart_product:
            temp_amount=(p.quantity*p.product.discounted_price)
            amount+=temp_amount
        
        data={
            'amount':amount,
            'totalamount':amount+shippingamount
        }
        return JsonResponse(data)


def mobile(request,data=None):
    if data==None:
        mobiles=Product.objects.filter(category='M')
    elif data=='Redmi' or data=='Motorolla' or data=='Apple' or data=='samsung':
        mobiles=Product.objects.filter(category='M').filter(brand=data)
    # print(mobiles[0].title)
    return render(request,'app/mobile.html',{'mobiles':mobiles})

def topwear(request,data=None):
    if data==None:
        topwears=Product.objects.filter(category='TW')
    elif data=='Nike' or data=='Puma' or data=='Amazon':
        topwears=Product.objects.filter(category='TW').filter(brand=data)
    # print(mobiles[0].title)
    return render(request,'app/topwear.html',{'topwears':topwears})

def bottomwear(request,data=None):
    if data==None:
        bottomwears=Product.objects.filter(category='BW')
    elif data=='Levi' or data=='Peter england':
        bottomwears=Product.objects.filter(category='BW').filter(brand=data)
    # print(mobiles[0].title)
    return render(request,'app/bottomwear.html',{'bottomwears':bottomwears})
        


# def customerregistration(request):
#  return render(request, 'app/customerregistration.html')

class CustomerRegistrationView(View):
    def get(self,request):
        form=CustomerRegistrationForm()
        return render(request,'app/customerregistration.html',{'form':form})
    
    def post(self,request):
        form=CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,'Congratulations !! You are Registered Successfully')
            form.save()
        return render(request,'app/customerregistration.html',{'form':form})
        
@login_required
def checkout(request):
    user=request.user
    add=Customer.objects.filter(user=user)
    cart_items=Cart.objects.filter(user=user)
    amount=0.0
    shipping_amount=70.0
    total_amount=0.0
    cart_product=[p for p in Cart.objects.all() if p.user==request.user]
    if cart_product:
        for p in cart_product:
            temp_amount=(p.quantity*p.product.discounted_price)
            amount+=temp_amount
        total_amount=amount+shipping_amount
    return render(request, 'app/checkout.html',{'add':add,'cart_item':cart_items,'totalamount':total_amount})

@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self,request):
        form=CustomerProfileForm()
        return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})
    
    def post(self,request):
        form=CustomerProfileForm(request.POST)
        if(form.is_valid()):
            usr=request.user
            name=form.cleaned_data['name']
            locality=form.cleaned_data['locality']
            city=form.cleaned_data['city']
            state=form.cleaned_data['state']
            zipcode=form.cleaned_data['zipcode']
            reg=Customer(user=usr,name=name,locality=locality,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,'Congratulation !! Profile Updated Successfully')
        return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})
        
@login_required
def payment_done(request):
    user=request.user
    custid=request.GET.get('custid')
    customer=Customer.objects.get(id=custid)
    cart=Cart.objects.filter(user=request.user)
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity).save()
        c.delete()
    return redirect("orders")
     