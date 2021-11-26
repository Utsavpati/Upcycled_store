
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator,MinValueValidator

# Create your models here.
State_choices=(
    ('bihar','bihar'),
    ('jharkhand','jharkhand'),
)

class Customer(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    locality=models.CharField(max_length=220)
    city=models.CharField(max_length=220)
    zipcode=models.IntegerField()
    state=models.CharField(choices=State_choices,max_length=50)

    def __str__(self):
        return self.name
        

category_choices=(
    ('M','Mobile'),
    ('L','Laptop'),
    ('TW','Topwear'),
)

class Product(models.Model):
    title=models.CharField(max_length=100)
    selling_price=models.FloatField()
    discounted_price=models.FloatField()
    description=models.TextField()
    brand=models.CharField(max_length=100)
    category=models.CharField(choices=category_choices,max_length=2)
    product_image=models.ImageField(upload_to='productimg')

    def __str__(self):
        return self.title
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.id
    
    @property
    def total_cost(self):
        return self.quantity*self.product.discounted_price


Status_choices=(('Accepted','Accepted'),
                ('Packed','Packed'),
                ('On the way','On the way'),
                ('Delivered','Deleivered'),
                ('Cancel','Cancel'))

class order_placed(models.Model):
        user=models.ForeignKey(User,on_delete=models.CASCADE)
        customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
        product=models.ForeignKey(Product,on_delete=models.CASCADE)
        quantity=models.PositiveIntegerField(default=1)
        ordered_date=models.DateTimeField(auto_now_add=True)
        status=models.CharField(max_length=50,choices=Status_choices,default='Pending')

        @property
        def total_cost(self):
            return self.quantity*self.product.discounted_price 


class merchant(models.Model):
    merch=models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    address=models.CharField(max_length=255)
    first=models.CharField(max_length=255)
    last=models.CharField(max_length=255)
    email=models.EmailField(max_length=25)
    
    def __str__(self) -> str:
        return f'{self.first} {self.last}'

