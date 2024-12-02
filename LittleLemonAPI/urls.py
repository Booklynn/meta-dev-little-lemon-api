from django.urls import path
from . import views

urlpatterns = [
    path('menu-items/category', views.CategoryView.as_view()),
    path('menu-items', views.MenuItemView.as_view()),
    path('menu-items/<int:pk>', views.MenuItemDetailView.as_view()),
    path('groups/manager/users', views.GroupManagerUserView.as_view()),
    path('groups/manager/users/<int:pk>', views.GroupManagerUserDestroyView.as_view()),
    path('groups/delivery-crew/users', views.GroupDeliveryCrewUserView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.GroupDeliveryCrewUserDestroyView.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
    path('orders', views.OrderView.as_view()),
    path('orders/<int:pk>', views.OrderDetailView.as_view()),
]
