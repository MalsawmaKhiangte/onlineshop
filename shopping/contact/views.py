from django.shortcuts import render
from django.core.mail import  send_mail
from django.conf import settings

def contact(request):

    if request.method == 'POST':
        message = request.POST['message']
        send_mail('Contact Form' , message , setting.EMAIL_HOST_USER , reciver , fail_silently=False , )
    return render(request, 'contact/mailme.html')

# Create your views here.
