from django.urls import path
from useradmin import views


app_name = "useradmin"

urlpatterns = [
    path("", views.dashboard2, name="dashboard2"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("products/", views.products, name="dashboard-products"),
    path("add-products/", views.add_product, name="dashboard-add-products"),
    path("edit-products/<pid>/", views.edit_product, name="dashboard-edit-products"),
    path("delete-products/<pid>/", views.delete_product, name="dashboard-delete-products"),
    path("orders/", views.orders, name="orders"),
    path("order_detail/<id>/", views.order_detail, name="order_detail"),
    path("change_order_status/<oid>/", views.change_order_status, name="change_order_status"),
    path("shop_page/", views.shop_page, name="shop_page"),
    path("reviews/", views.reviews, name="reviews"),
    path("settings/", views.settings, name="settings"),
    path("change_password/", views.change_password, name="change_password"),
    path('estimate/', views.estimate, name='Estimate'),
    path('charges/', views.charges, name='charges'),
    path('invoice/', views.invoice, name='invoice'),
    path('update-paid-amount/<int:order_id>/', views.update_paid_amount, name='update_paid_amount'),
    path('expenditure-dashboard/', views.expenditure_dashboard, name='expenditure_dashboard'),
    path('add-expenditure/', views.add_expenditure, name='add_expenditure'),
    path('delete-expenditure/<int:expenditure_id>/', views.delete_expenditure, name='delete_expenditure'),
    path('update-expenditure/<int:expenditure_id>/', views.update_expenditure, name='update_expenditure'),



]