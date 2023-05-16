from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(SignUp)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)

class SignUpAdmin(admin.ModelAdmin):
    list_display = ("id" ,"first_name", "last_name")
    list_display_links = ("first_name", "last_name")

class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "product_brand", "product_name")