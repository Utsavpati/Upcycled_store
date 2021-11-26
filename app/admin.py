from django.contrib import admin
from .models import Customer,Product,Cart,order_placed
# Register your models here.
@admin.register(Customer)
class Custormeradmin(admin.ModelAdmin):
    list_display=['id','user','name','locality','city','zipcode','state']

@admin.register(Product)
class Productadmin(admin.ModelAdmin):
    list_display=['id','title','selling_price','discounted_price','description','brand','category','product_image']

@admin.register(Cart)
class Cartadmin(admin.ModelAdmin):
    list_display=['id','user','product','quantity']


@admin.register(order_placed)
class Orderplacedadmin(admin.ModelAdmin):
    list_display=['id','user','customer','product','quantity','ordered_date','status']