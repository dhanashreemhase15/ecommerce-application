from django.shortcuts import render,HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from ecomm_app.models import product, Cart , Order
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail
# Create your views here.
def about(request):
    return HttpResponse("Hello from about page")

def contact(request):
    return HttpResponse("<h1>Hello from contact page</h1>")

def edit(request,rid):
    return HttpResponse("id to be edited:"+rid)

def addition(request,x1,x2):
    t=int(x1)+int(x2)
    t=str(t)
    return HttpResponse("Addition is :"+t)

def hello(request):
    context={}
    context['greet']="Hello,we are learning DTL"
    context['x']=100
    context['y']=20
    context['l']=[10,20,30,40,50]
    context['products']=[
	    {'id':1,'name':'samsung','cat':'mobile','price':2000},
	    {'id':2,'name':'jeans','cat':'clothes','price':500},
	    {'id':3,'name':'vivo','cat':'mobile','price':1500},
        ]
    return render(request,'hello.html',context)

def home(request):
   # userid= request.user.id
   # print("id of logged in user: ",userid)
   #print("result: ",request.user.is_authenticated)
   p=product.objects.filter(is_active=True)
   print(p)
   context={}
   context['products']=p
   return render(request,'index.html',context)

def product_details(request,pid):
    p=product.objects.filter(id=pid)
    print(p)
    context={}
    context['products']=p
    return render(request,'product_details.html',context)

def register(request):
    if request.method=='POST':
        uname =request.POST['uname']
        upass =request.POST['upass']
        ucpass =request.POST['ucpass']
        context={}
        if uname=="" or upass=="" or ucpass=="":
            context['errmsg']="Fields can not be Empty"
            return render (request,'register.html',context)
        elif upass != ucpass:
            context['errmsg']="Password  & confirm password didn't match"
            return render (request,'register.html',context)
        else:
         try:
                    u=User.objects.create(password=upass,username=uname,email=uname)
                    u.set_password(upass)
                    u.save()
                    context['success']="User created successfully !! Please Login"
                    return render(request,'register.html',context)
           
         # return HttpResponse("User Created Successfully")
         except Exception:
            context['errmsg']="User with same username already exists"
            return render(request,'register.html',context)
    else:
         return render(request,'register.html')
def user_login(request):
     if request.method =='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        #print(uname,"-",upass)
        #return HttpResponse("Data is fetched")
        context={}
        if uname=="" or upass=="":
            context['errmsg']="Fields should not be Empty"
            return render(request,'login.html',context)
        else:
            u=authenticate(username=uname,password=upass)
            #print(u)
            if u is not None:
                login(request,u)
                return redirect("/home")
            else:
                context['errmsg']="invalid Username and Password"
                return render(request,"login.html",context)
     else:
         return render(request,'login.html')
     
def user_logout(request):
    logout(request)
    return redirect('/home')

def catfilter(request,cv):
    q1=Q(is_active=True)
    q2=Q(cat=cv)
    p=product.objects.filter(q1 & q2)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def sort(request, sv):
        if sv=='0':
            col='price'
        else:
            col='-price'
        p=product.objects.filter(is_active=True).order_by(col)
        context={}
        context['products']=p
        return render(request,'index.html',context)

def range(request):
    min=request.GET['min']
    max=request.GET['max']
    print(min)
    print(max)
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=True)
    p=product.objects.filter(q1 & q2 & q3)
    context={}
    context['products']=p
    return render(request,'index.html',context)
    return HttpResponse("Values Fetched")

def addtocart(request,pid):
    if request.user.is_authenticated:
        userid=request.user.id
        # print(pid)
        #print(userid)
        u=User.objects.filter(id=userid)
        p=product.objects.filter(id=pid)
        q1=Q(uid=u[0])
        q2=Q(pid=p[0])
        c=Cart.objects.filter(q1 & q2)
        n=len(c)
        context={}
        context['products']=p
        if n==1:
            context['msg']='product already exist in the cart'
        else:
             c=Cart.objects.create(uid=u[0],pid=p[0])
             c.save()
             context['success']="product added Successfully to cart"
        return render(request,'product_details.html',context)
        #return HttpResponse("Product added to cart")
    else:
        return redirect('/login')

def viewcart(request):
    c=Cart.objects.filter(uid=request.user.id)
    #print(c)
    s=0
    np=len(c)
    #print(np)
    for x in c:
        s=s+ x.pid.price*x.qty
    print(s)
    context={}
    context['data']=c
    context['total']=s
    context['n']=np
    return render(request,'cart.html',context)
def remove(request,cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')
def updateqty(request,qv,cid):
    c=Cart.objects.filter(id=cid)
    if qv=='1':
        t=c[0].qty + 1
        c.update(qty=t)
    else:
        if c[0].qty>1:
            t=c[0].qty -1
            c.update(qty=t)

    #return HttpResponse("qyantity")
    return redirect('/viewcart')

def placeorder(request):
    userid=request.user.id
    c=Cart.objects.filter(uid=userid)
    print(c)
    oid=random.randrange(1000,9999)
    #print(oid)
    for x in c:
        o=Order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
        o.save()
        x.delete()
        orders=Order.objects.filter(uid=request.user.id)
        context={}
        context['data']=orders
        s=0
        np=len(orders)
        for x in orders:
            s=s+x.pid.price*x.qty
            context['total']=s
            context['n']=np

    #return HttpResponse("Order Confirmed")
    return render(request,'placeorder.html',context)

def makepayment(request):
    uemail=request.user.username
    # print(uemail)
    orders=Order.objects.filter(uid=request.user.id)
    s=0
    np=len(orders)
    for x in orders:
        s=s + x.pid.price*x.qty
        oid=x.order_id

    client = razorpay.Client(auth=("rzp_test_kFWjLiDcgADQcW", "qvD6wxlCMk3UatZp6KxJgfZD"))
    data = { "amount": s*100, "currency": "INR", "receipt": "oid" }
    payment = client.order.create(data=data)
    #return HttpResponse("Success")
    #print(payment)
    context={}
    context['data']=payment
    context['uemail']=uemail
    return render(request,'pay.html',context)

def sendusermail(request,uemail):
    # print("--------------",uemail)
    msg="order details"
    send_mail(
        'Ekart -order placed successfully',
        msg,
        'dhanashreemhase15@gmail.com',
        [uemail],
        fail_silently=False,
    )
    return HttpResponse("mail send successfully")