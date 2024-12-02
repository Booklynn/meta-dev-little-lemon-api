from django.contrib import admin
from .models import Cart, Category, MenuItem, Order

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title')

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'featured', 'category')

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'menuitem', 'quantity', 'unit_price', 'price')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'delivery_crew', 'status', 'total', 'date')

admin.site.register(Category, CategoryAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
