from django.db import models
from shop.models import Product
from decimal import Decimal
from django.core.validators import MinValueValidator , MaxValueValidator
from coupons.models import Coupon

class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    phone = models.IntegerField(default=0)
    pin_code = models.CharField(max_length=20)
    created =models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    coupon = models.ForeignKey(Coupon , on_delete=models.SET_NULL , related_name='orders', null=True , blank=True)
    discount = models.IntegerField(default=0 ,
                                    validators=[MaxValueValidator(0),
                                                MaxValueValidator(100)])

    class Meta:
        ordering =('-created',)

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        total_cost =  sum(item.get_cost() for item in self.items.all())
        return int(total_cost - total_cost * (self.discount/Decimal('100')))

class OrderItem(models.Model):
    order = models.ForeignKey(Order , on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product , on_delete=models.CASCADE, related_name='order_items' )
    price = models.DecimalField(max_digits=10 , decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity


# Create your models here.
