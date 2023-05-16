from django.urls import path, include
from .views import *
from home import views

urlpatterns = [
    path('', views.index, name="index"),
    path('header', views.header, name='header'),
    path('footer', views.footer, name='footer'),

    path('signin/', views.signin, name="signin"),
    path('signup/', views.signup, name="signup"),
    path('logout/', views.logout_view, name="logout_view"),

    path('cart/add/<int:product_id>', views.add_cart, name='add_cart'),
    path('cart', views.cart_detail, name='cart_detail'),
    path('cart/remove/<int:product_id>', views.cart_remove, name='cart_remove'),
    path('cart/remove_product/<int:product_id>', views.cart_remove_product, name='cart_remove_product'),

    
]