from datetime import datetime
from rest_framework.exceptions import ValidationError
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from .permissions_extensions import IsManager, IsDeliveryCrew
from .models import Cart, Category, MenuItem, Order, OrderItem
from .serializers import CartSerializer, CategorySerializer, MenuItemSerializer, OrderSerializer, UserSerializer

class CategoryView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all().order_by('id')
    serializer_class = MenuItemSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ('name',)
    ordering_fields = ('name', 'price',)
    search_fields = ('name',)

    def get_permissions(self):
        if self.request.method == 'POST':
           return [IsManager()]
        return []

class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsManager()]
        return []

class GroupManagerUserView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser | IsManager]
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('id')
        if not user_id:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, pk=user_id)
        try:
            managers = Group.objects.get(name='Manager')
        except Group.DoesNotExist:
            return Response({"detail": "The Manager group does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        if user in managers.user_set.all():
            return Response({"detail": f"User {user.username} is already added to manager group."}, status=status.HTTP_200_OK)
        
        managers.user_set.add(user)
        return Response({"detail": f"User {user.username} added to manager group."}, status=status.HTTP_201_CREATED)

class GroupManagerUserDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser | IsManager]
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = UserSerializer

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = get_object_or_404(User, pk=user_id)
        try:
            managers = Group.objects.get(name='Manager')
        except Group.DoesNotExist:
            return Response({"detail": "The Manager group does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        if user not in managers.user_set.all():
            return Response({"detail": f"User {user.username} is not in the manager group."}, status=status.HTTP_404_NOT_FOUND)
        
        managers.user_set.remove(user)
        return Response({"detail": f"User {user.username} removed from manager group."}, status=status.HTTP_200_OK)
    
class GroupDeliveryCrewUserView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser | IsManager]
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('id')
        if not user_id:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, pk=user_id)
        try:
            delivery_crew = Group.objects.get(name='Delivery crew')
        except Group.DoesNotExist:
            return Response({"detail": "The Delivery crew group does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        if user in delivery_crew.user_set.all():
            return Response({"detail": f"User {user.username} is already added to delivery crew group."}, status=status.HTTP_200_OK)
        
        delivery_crew.user_set.add(user)
        return Response({"detail": f"User {user.username} added to delivery crew group."}, status=status.HTTP_201_CREATED)
    
class GroupDeliveryCrewUserDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser | IsManager]
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = UserSerializer

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = get_object_or_404(User, pk=user_id)
        try:
            delivery_crew = Group.objects.get(name='Delivery crew')
        except Group.DoesNotExist:
            return Response({"detail": "The Delivery crew group does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        if user not in delivery_crew.user_set.all():
            return Response({"detail": f"User {user.username} is not in the delivery crew group."}, status=status.HTTP_404_NOT_FOUND)
        
        delivery_crew.user_set.remove(user)
        return Response({"detail": f"User {user.username} removed from delivery crew group."}, status=status.HTTP_200_OK)
    
class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        menuitem_id = self.request.data.get('menuitem_id')

        menuitem = get_object_or_404(MenuItem, pk=menuitem_id)
        unit_price = menuitem.price
        quantity = self.request.data.get('quantity')

        price = unit_price * (int(quantity))
        serializer.save(user=self.request.user, unit_price=unit_price, price=price)

    def delete(self, request):
        user = self.request.user
        Cart.objects.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists() or user.is_staff:
            return Order.objects.all().order_by('id')
    
        if user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=user).order_by('id')

        return Order.objects.filter(user=user).order_by('id')
    
    def perform_create(self, serializer):
        if self.request.user.groups.filter(name='Delivery crew').exists():
            raise ValidationError({"detail": "Delivery crew cannot place an order."})

        cart_items = Cart.objects.filter(user=self.request.user)

        if not cart_items.exists():
            raise ValidationError({"detail": "Your cart is empty. Please add items before placing an order."})

        total = sum([cart_item.price for cart_item in cart_items])
        today_date = datetime.now().strftime("%Y-%m-%d")
        serializer.save(user=self.request.user, total=total, date=today_date)

        for item in cart_items:
            OrderItem.objects.create(order=serializer.instance, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, price=item.price)
        cart_items.delete()

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request.method == 'PUT':
            if self.request.user.groups.filter(name='Delivery crew').exists():
                return [IsDeliveryCrew()]
            return [IsManager()]
        
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsManager()]

        return [IsAuthenticated()]
            
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists() or user.is_staff:
            return Order.objects.all()
        
        if user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=user)
        
        return Order.objects.filter(user=user)

    def perform_update(self, serializer):
        user = self.request.user

        if user.groups.filter(name='Delivery crew').exists():
            if 'status' not in self.request.data:
                raise ValidationError({"detail": "Delivery crew can only update the status."})
            serializer.save(status=self.request.data.get('status'))
        
        elif user.groups.filter(name='Manager').exists() or user.is_staff:
            delivery_crew_name = self.request.data.get('delivery_crew')
            delivery_crew = get_object_or_404(User, username=delivery_crew_name) if delivery_crew_name else None
            if delivery_crew and not delivery_crew.groups.filter(name='Delivery crew').exists():
                raise ValidationError({"detail": "The selected user is not a delivery crew."})

            serializer.save(
                status=self.request.data.get('status'),
                delivery_crew=delivery_crew
            )
