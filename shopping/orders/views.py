from django.shortcuts import render , redirect , get_object_or_404
from .models import OrderItem , Order
from .forms import OrderCreateForm
from cart.cart import Cart
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from . import Checksum
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
import weasyprint
from .utils import VerifyPaytmResponse
from weasyprint import HTML
from django.views.generic import View
from django.template.loader import get_template
from .utils import render_to_pdf


def order_create(request):
    cart =Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order , product=item['product'] , price=item['price'] , quantity= item['quantity'] )
            #order_created.delay(order.id)

            data_dict = {
                'MID': settings.PAYTM_MERCHANT_ID,
                'INDUSTRY_TYPE_ID': settings.PAYTM_INDUSTRY_TYPE_ID,
                'WEBSITE': settings.PAYTM_WEBSITE,
                'CHANNEL_ID': settings.PAYTM_CHANNEL_ID,
                'CALLBACK_URL': settings.PAYTM_CALLBACK_URL,
                'MOBILE_NO': str('phone'),
                'EMAIL': order.email,
                'CUST_ID': '123123',
                'ORDER_ID':str(order.id),
                'TXN_AMOUNT': str(order.get_total_cost()),
                } # This data should ideally come from database
            data_dict['CHECKSUMHASH'] = Checksum.generate_checksum(data_dict, settings.PAYTM_MERCHANT_KEY)
            context = {
                        'payment_url': settings.PAYTM_PAYMENT_GATEWAY_URL,
                        'comany_name': settings.PAYTM_COMPANY_NAME,
                        'data_dict': data_dict
                        }
            return render(request, 'orders/order/payment.html', context)
            #return render(request , 'orders/order/created.html' , {'order': order})

    else:
        form = OrderCreateForm()
    return render(request , 'orders/order/create.html', {'cart':cart , 'form':form})


@csrf_exempt
def response(request):

    resp = VerifyPaytmResponse(request)
    if resp['verified']:
        # save success details to db; details in resp['paytm']
        return redirect('orders:done')
    else:
        # check what happened; details in resp['paytm']
        return HttpResponse("<center><h1>Transaction Failed</h1><center>")

def done(request):
    cart = Cart(request)
    order = Order.objects.latest('id')
    order.paid = True
    order.save()
    cart.clear()
    #html = render_to_string('orders/orderpdf.html' , {'order':order})
    return render(request , 'orders/order/pdf.html', {'order':order})


@staff_member_required
def admin_order_detail(request , order_id):
    order = get_object_or_404(Order , id=order_id)
    return render(request , 'admin/orders/order/detail.html', {'order':order})

@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html' , {'order':order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=\"order_{}.pdf'.format(order.id)
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + '/css/pdf.css')])
    return response

def generate_pdf(request , *args , **kwargs):
    order = Order.objects.latest('id')
    template = get_template('orders/order/invoice.html')
    html = template.render({'order':order})
    pdf = render_to_pdf('orders/order/invoice.html', {'order':order})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Invoice_%s.pdf" %(order.id)
        content = "inline; filename='%s'" %(filename)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        weasyprint.HTML(string=html).write_pdf(response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + '/css/pdf.css')])
        return response
    return HttpResponse("Not found")
