from django.contrib import admin
from .models import Coupon

class CouponAdmin(admin.ModelAdmin):
    list_display  = ['code' , 'valid_from' , 'valid_till' , 'discount' , 'active']
    list_filter = ['code' , 'active' , 'valid_from' , 'valid_till']
    search_fields = ['code']
admin.site.register(Coupon , CouponAdmin)

# Register your models here.
