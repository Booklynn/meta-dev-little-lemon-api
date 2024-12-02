from decimal import Decimal
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User

from .models import Cart, Category, MenuItem, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta():
        model = Category
        fields = ['id', 'slug', 'title']

        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=['slug', 'title']
            )
        ]

class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'featured', 'category_id', 'category']

        validators = [
            UniqueTogetherValidator(
                queryset=MenuItem.objects.all(),
                fields=['name', 'category_id']
            )
        ]
        
        extra_kwargs = {
            'price': {'min_value': Decimal('1.0')}
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active']

        extra_kwargs = {
            'id': {'read_only': False},
            'username': {'read_only': True},
            'first_name': {'read_only': True},
            'last_name': {'read_only': True},
            'email': {'read_only': True},
            'is_active': {'read_only': True}
        }

class CartSerializer(serializers.ModelSerializer):
    menuitem_id = serializers.IntegerField()
    menu_name = serializers.CharField(source='menuitem.name', read_only=True)

    class Meta:
        model = Cart
        fields = ['menuitem_id', 'menu_name', 'quantity', 'unit_price', 'price']
            
        extra_kwargs = {
            'quantity': {'min_value': 1},
            'unit_price': {'read_only': True},
            'price': {'read_only': True}
        }


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):
    order_item = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_item']

        extra_kwargs = {
            'user': {'read_only': True},
            'delivery_crew': {'read_only': True},
            'status': {'read_only': True},
            'total': {'read_only': True},
            'date': {'read_only': True}
        }

    def get_order_item(self, obj):
        order_items = obj.orderitem_set.all()
        context = self.context if 'request' in self.context else {}
        return OrderItemSerializer(order_items, many=True, context=context).data

    