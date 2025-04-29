from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from core.models import CartOrder, CartOrderProducts, Product, Category, ProductReview, Expenditure
from userauths.models import Profile, User
from useradmin.forms import AddProductForm
from useradmin.decorators import admin_required
import datetime
from django.utils import timezone
from django.core.mail import send_mail
import json
from decimal import Decimal


@admin_required
@csrf_exempt
def add_expenditure(request):
    if request.method == 'POST':
        category = request.POST.get('category')  # Updated to match the renamed field
        amount = request.POST.get('amount')
        Expenditure.objects.create(category=category, amount=amount)
    return redirect('useradmin:expenditure_dashboard')

@admin_required
def delete_expenditure(request, expenditure_id):
    expenditure = get_object_or_404(Expenditure, id=expenditure_id)
    expenditure.delete()
    return redirect('useradmin:expenditure_dashboard')

@admin_required
def update_expenditure(request, expenditure_id):
    expenditure = get_object_or_404(Expenditure, id=expenditure_id)

    if request.method == 'POST':
        category = request.POST.get('category')
        amount = request.POST.get('amount')

        expenditure.category = category
        expenditure.amount = amount
        expenditure.save()

        return redirect('useradmin:expenditure_dashboard')

    context = {
        'expenditure': expenditure,
        'categories': Expenditure.CATEGORY_CHOICES,
    }
    return render(request, 'useradmin/update_expenditure.html', context)




@admin_required
def expenditure_dashboard(request):
    # Get all expenditures
    expenditures = Expenditure.objects.all()
    total_spent = sum(Decimal(exp.amount) for exp in expenditures)

    # Calculate totals by category
    totals_by_category = {
        category: sum(Decimal(exp.amount) for exp in expenditures if exp.category == category)
        for category, _ in Expenditure.CATEGORY_CHOICES
    }

    # Calculate money in the bank
    this_month = datetime.datetime.now().month
    monthly_revenue = CartOrder.objects.filter(order_date__month=this_month).aggregate(price=Sum("price"))['price'] or Decimal('0.00')
    unpaid_orders_total = CartOrder.objects.filter(paid_status=False).aggregate(total_unpaid=Sum("price"))['total_unpaid'] or Decimal('0.00')
    money_in_bank = monthly_revenue - unpaid_orders_total

    # Calculate remaining balance
    remaining_balance = money_in_bank - total_spent
    danger_zone = remaining_balance < (Decimal('0.2') * money_in_bank)

    context = {
        'expenditures': expenditures,
        'totals_by_category': totals_by_category,
        'money_in_bank': money_in_bank,
        'remaining_balance': remaining_balance,
        'danger_zone': danger_zone,
    }
    return render(request, 'useradmin/expenditure_dashboard.html', context)



@admin_required
def update_paid_amount(request, order_id):
    if request.method == "POST":
        data = json.loads(request.body)  # Parse JSON body
        amount_paid = data.get("amount_paid", 0.00)
        order = get_object_or_404(CartOrder, id=order_id)
        order.amount_already_paid = amount_paid
        order.save()

        # Log or print for debugging
        print(f"Order {order_id} updated with amount: {amount_paid}")

        return JsonResponse({"success": True, "amount_paid": amount_paid})
    return JsonResponse({"success": False, "error": "Invalid request method"})


@admin_required
def invoice(request):
    return render(request, 'useradmin/invoice.html')

@admin_required
def estimate(request):
    return render(request, 'useradmin/estimate.html')

@admin_required
def charges(request):
    return render(request, 'useradmin/charges.html')


@admin_required
def dashboard(request):
    # Aggregate total revenue
    revenue = CartOrder.objects.aggregate(price=Sum("price"))['price'] or 0
    total_orders_count = CartOrder.objects.count()
    all_products = Product.objects.all()
    all_categories = Category.objects.all()
    new_customers = User.objects.all().order_by("-id")[:6]
    latest_orders = CartOrder.objects.all()

    # Calculate monthly revenue
    this_month = datetime.datetime.now().month
    monthly_revenue = CartOrder.objects.filter(order_date__month=this_month).aggregate(price=Sum("price"))['price'] or 0

    # Calculate total amount of unpaid orders
    unpaid_orders_total = CartOrder.objects.filter(paid_status=False).aggregate(total_unpaid=Sum("price"))['total_unpaid'] or 0

    # Calculate money in the bank
    money_in_the_bank = monthly_revenue - unpaid_orders_total

    context = {
        "monthly_revenue": monthly_revenue,
        "revenue": revenue,
        "all_products": all_products,
        "all_categories": all_categories,
        "new_customers": new_customers,
        "latest_orders": latest_orders,
        "total_orders_count": total_orders_count,
        "unpaid_orders_total": unpaid_orders_total,
        "money_in_the_bank": money_in_the_bank,  # Added context
    }
    return render(request, "useradmin/dashboard.html", context)

@admin_required
def dashboard2(request):
    # Aggregate total revenue from all orders
    revenue = CartOrder.objects.aggregate(price=Sum("price"))['price'] or 0

    # Count total orders
    total_orders_count = CartOrder.objects.count()

    # Retrieve all products and categories
    all_products = Product.objects.all()
    all_categories = Category.objects.all()

    # Get the most recent 6 customers
    new_customers = User.objects.all().order_by("-id")[:6]

    # Retrieve all orders (you might want to filter them if the list is large)
    latest_orders = CartOrder.objects.all()

    # Calculate monthly revenue (sum of prices for orders placed in the current month)
    this_month = datetime.datetime.now().month
    monthly_revenue = CartOrder.objects.filter(order_date__month=this_month).aggregate(price=Sum("price"))['price'] or 0

    # Calculate total amount of unpaid orders (sum of prices for orders with paid_status=False)
    unpaid_orders_total = CartOrder.objects.filter(paid_status=False).aggregate(total_unpaid=Sum("price"))['total_unpaid'] or 0

    # Calculate money in the bank (revenue minus unpaid orders)
    money_in_the_bank = revenue - unpaid_orders_total  # Use total revenue, not just monthly revenue

    context = {
        "monthly_revenue": monthly_revenue,
        "revenue": revenue,
        "all_products": all_products,
        "all_categories": all_categories,
        "new_customers": new_customers,
        "latest_orders": latest_orders,
        "total_orders_count": total_orders_count,
        "unpaid_orders_total": unpaid_orders_total,
        "money_in_the_bank": money_in_the_bank,  # Added to the context
    }

    return render(request, "useradmin/dashboard2.html", context)


@admin_required
def products(request):
    all_products = Product.objects.all()
    all_categories = Category.objects.all()

    context = {
        "all_products": all_products,
        "all_categories": all_categories,
    }
    return render(request, "useradmin/products.html", context)

@admin_required
def add_product(request):
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            form.save_m2m()
            messages.success(request, "Product added successfully!")
            return redirect("useradmin:dashboard-products")
    else:
        form = AddProductForm()

    context = {
        'form': form
    }
    return render(request, "useradmin/add-products.html", context)

@admin_required
def edit_product(request, pid):
    product = get_object_or_404(Product, pid=pid)

    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect("useradmin:dashboard-products")
    else:
        form = AddProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
    }
    return render(request, "useradmin/edit-products.html", context)

@admin_required
def delete_product(request, pid):
    product = get_object_or_404(Product, pid=pid)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect("useradmin:dashboard-products")

@admin_required
def orders(request):
    orders = CartOrder.objects.all()
    one_week_ago = timezone.now() - timezone.timedelta(weeks=1)

    # Check for unpaid orders and send reminders only if no reminder was sent in the last 7 days
    for order in orders:
        if not order.paid_status:
            # If no reminder has ever been sent or it's been more than 7 days since the last reminder
            if not order.last_reminder_sent or order.last_reminder_sent < one_week_ago:
                send_reminder_email(order)
                # Update the last reminder sent timestamp
                order.last_reminder_sent = timezone.now()
                order.save()

    context = {
        'orders': orders,
    }
    return render(request, "useradmin/orders.html", context)



# Helper function to send email reminders for unpaid orders
def send_reminder_email(order):
    subject = 'Friendly Reminder: Your Unpaid Order is Waiting!'
    message = f"""
    Dear {order.full_name},

    We hope this message finds you well!

    We noticed that you have an unpaid order in your account, and we wanted to send a friendly reminder to complete the payment and finalize your purchase.

    Order Summary:
    Order Number: {order.oid}
    Order Date: {order.date.strftime('%d %B %Y')}
    Total Amount Due: Ksh {order.price}.

    If you have any questions or need assistance, feel free to reply to this email or contact our customer support at 0769415419.

    We look forward to completing your order!

    Thank you for choosing us.

    Best regards,
    Evely Fresh Ventures LTD
    0769415419 or everfreshfruits1@gmail.com
    https://www.evelyfreshventures.com
    """

    send_mail(subject, message, 'everfreshfruits1@gmail.com', [order.email])
    print(f'Reminder email sent for order {order.oid}')

@admin_required
def order_detail(request, id):
    order = get_object_or_404(CartOrder, id=id)
    order_items = CartOrderProducts.objects.filter(order=order)
    context = {
        'order': order,
        'order_items': order_items
    }
    return render(request, "useradmin/order_detail.html", context)


@admin_required
@csrf_exempt
def change_order_status(request, oid):
    order = get_object_or_404(CartOrder, oid=oid)
    if request.method == "POST":
        status = request.POST.get("status")
        if status:
            order.product_status = status
            order.save()
            messages.success(request, f"Order status changed to {status}")
        else:
            messages.error(request, "Status is required.")
    return redirect("useradmin:order_detail", order.id)

@admin_required
def shop_page(request):
    products = Product.objects.filter(user=request.user)
    revenue = CartOrder.objects.filter(paid_status=True).aggregate(price=Sum("price"))['price'] or 0
    total_sales = CartOrderProducts.objects.filter(order__paid_status=True).aggregate(qty=Sum("qty"))['qty'] or 0

    context = {
        'products': products,
        'revenue': revenue,
        'total_sales': total_sales,
    }
    return render(request, "useradmin/shop_page.html", context)

@admin_required
def reviews(request):
    reviews = ProductReview.objects.all()
    context = {
        'reviews': reviews,
    }
    return render(request, "useradmin/reviews.html", context)

@admin_required
def settings(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":
        image = request.FILES.get("image")
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        bio = request.POST.get("bio")
        address = request.POST.get("address")
        country = request.POST.get("country")

        if image:
            profile.image = image
        profile.full_name = full_name
        profile.phone = phone
        profile.bio = bio
        profile.address = address
        profile.country = country

        profile.save()
        messages.success(request, "Profile Updated Successfully")
        return redirect("useradmin:settings")

    context = {
        'profile': profile,
    }
    return render(request, "useradmin/settings.html", context)

@admin_required
def change_password(request):
    user = request.user

    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_new_password = request.POST.get("confirm_new_password")

        if confirm_new_password != new_password:
            messages.error(request, "Confirm Password and New Password Do Not Match")
            return redirect("useradmin:change_password")

        if check_password(old_password, user.password):
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password Changed Successfully")
            return redirect("useradmin:change_password")
        else:
            messages.error(request, "Old password is not correct")
            return redirect("useradmin:change_password")

    return render(request, "useradmin/change_password.html")


