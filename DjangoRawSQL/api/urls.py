from django.urls import path

from . import views

urlpatterns = [
    path("products/", views.ProductListView.as_view()),
    path("products/<int:pk>/", views.ProductDetailView.as_view()),
    path("products/<int:pk>/reserve/", views.ProductReserveView.as_view()),
    path("orders/", views.OrderCreateView.as_view()),
]
