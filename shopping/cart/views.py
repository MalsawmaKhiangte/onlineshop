from django.shortcuts import render , get_object_or_404 ,redirect
from django.views.decorators.http import require_POST
from shop.models import Product
from .forms import CartAddProductForm
from .cart import Cart
from coupons.forms import CouponApplyForm

@require_POST
def cart_add(request , product_id):
    cart = Cart(request)
    product = get_object_or_404(Product , id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product , quantity=cd['quantity'] , quantity_update=cd['update'])
    return redirect('cart:cart_detail')

def cart_remove(request , product_id):
    cart = Cart(request)
    product = get_object_or_404(Product , id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['quantity_update_form'] = CartAddProductForm(initial = {'quantity':item['quantity'] , 'update':True})
    coupon_apply_form = CouponApplyForm()
    return render(request , 'cart/detail.html' , {'cart':cart , 'coupon_apply_form': coupon_apply_form})
# Create your views here.
