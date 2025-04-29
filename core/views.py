from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
import stripe
import datetime
from taggit.models import Tag
from core.models import Coupon, Product, Category, Vendor, CartOrder, CartOrderProducts, ProductReview, wishlist_model, Address
from userauths.models import ContactUs, Profile
from core.forms import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import calendar
from django.views.decorators.http import require_POST
from django.db.models import Count, Avg
from django.db.models.functions import ExtractMonth
from django.core import serializers
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from twilio.rest import Client
from django.db.models import Q

def send_sms(to, body):
    # Initialize Twilio client
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    try:
        message = client.messages.create(
            body=body,
            from_=settings.TWILIO_PHONE_NUMBER,  # Use settings.TWILIO_WHATSAPP_NUMBER for WhatsApp
            to=to
        )
        print(f"SMS sent to {to}: {message.sid}")
    except Exception as e:
        print(f"Error sending SMS: {e}")


def send_whatsapp(to, body):
    # Initialize Twilio client
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    try:
        message = client.messages.create(
            body=body,
            from_=settings.TWILIO_WHATSAPP_NUMBER,  # Twilio WhatsApp sandbox number
            to=f"whatsapp:{to}"
        )
        print(f"WhatsApp message sent to {to}: {message.sid}")
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")

def order_detail(request, id):
    order = get_object_or_404(CartOrder, user=request.user, id=id)
    order_items = CartOrderProducts.objects.filter(order=order)
    total_sum = sum([item.total for item in order_items])

    # Check if the email has already been sent
    if not order.email_sent:
        # Prepare the email context and render the message
        email_context = {
            "user": request.user,
            "order": order,
            "order_items": order_items,
            "total_sum": total_sum,
        }
        email_message = render_to_string('core/order_confirmation.html', email_context)

        # Send the email
        send_mail(
            subject=f"Order Confirmation - INV-{order.id}",
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            html_message=email_message
        )
        print("Email sent to:", request.user.email)

        # Send notification email to yourself
        send_mail(
            subject=f"New Order Placed - {request.user.username}",
            message=f"Customer {request.user.username} ({request.user.email}) has placed an order. Please check.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['alvotheboss@gmail.com', settings.DEFAULT_FROM_EMAIL]  # or use [settings.DEFAULT_FROM_EMAIL]
        )


        # Mark the order as having the email sent
        order.email_sent = True
        order.save()

    # Get the customer phone number from the Profile model
    customer_profile = get_object_or_404(Profile, user=request.user)
    customer_phone_number = customer_profile.phone

    # Prepare the SMS/WhatsApp message
    sms_message = f"Thank you for your order #{order.id}! Total: {total_sum}."

    # Send SMS
    if customer_phone_number:
        send_sms(customer_phone_number, sms_message)
    else:
        print("Customer phone number is missing.")

    # Send WhatsApp (optional)
    # Uncomment this if you want to send via WhatsApp
    send_whatsapp(customer_phone_number, sms_message)

    # Render the order details page
    context = {
        "order_items": order_items,
        "order": order,
        "total_sum": total_sum,
    }

    return render(request, 'core/order-detail.html', context)

@login_required
@require_POST
def pay_later(request):
    # Clear the cart from the session
    if 'cart_data_obj' in request.session:
        del request.session['cart_data_obj']

    # Get the latest order placed by the user (assuming it was just placed)
    latest_order = CartOrder.objects.filter(user=request.user).latest('id')
    order_items = CartOrderProducts.objects.filter(order=latest_order)
    total_sum = sum([item.total for item in order_items])

    # Check if the email has already been sent
    if not latest_order.email_sent:
        # Prepare the email context and render the message
        email_context = {
            "user": request.user,
            "order": latest_order,
            "order_items": order_items,
            "total_sum": total_sum,
        }
        email_message = render_to_string('core/order_confirmation.html', email_context)

        # Send the email to the customer
        send_mail(
            subject=f"Order Confirmation - INV-{latest_order.id}",
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            html_message=email_message,
        )

        # Send notification email to yourself
        send_mail(
            subject=f"New Order Placed - {request.user.username}",
            message=f"Customer {request.user.username} ({request.user.email}) has placed an order. Please check.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['alvotheboss@gmail.com', settings.DEFAULT_FROM_EMAIL]  # or use [settings.DEFAULT_FROM_EMAIL]
        )

        # Mark the order as having the email sent
        latest_order.email_sent = True
        latest_order.save()

    # Optionally, add a success message to indicate that the order was placed
    messages.success(request, "Your order is successfully placed and waiting for payment to be completed. You can pay later. A confirmation email has been sent to your inbox.")

    # Redirect to a suitable page (e.g., cart view or home page)
    return render(request, 'core/payment-completed.html')


@csrf_exempt
def payment_completed(request, oid):
    if request.method == "POST":
        reference = request.POST.get('reference')

        try:
            order = Order.objects.get(oid=oid)
            order.status = "Completed"
            order.save()
            send_order_confirmation_email(order)

            return JsonResponse({'status': 'success'})

        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)




@login_required
def index(request):
    products = Product.objects.filter(product_status="published", featured=True).order_by("-id")

    context = {
        "products":products
    }

    return render(request, 'core/index.html', context)
def product_list_view(request):
    products = Product.objects.filter(product_status="published").order_by("-id")
    tags = Tag.objects.all().order_by("-id")[:6]

    context = {
        "products":products,
        "tags":tags,
    }

    return render(request, 'core/product-list.html', context)

def category_list_view(request):
    categories = Category.objects.all()

    context = {
        "categories":categories
    }
    return render(request, 'core/category-list.html', context)
def category_product_list__view(request, cid):

    category = Category.objects.get(cid=cid) # food, Cosmetics
    products = Product.objects.filter(product_status="published", category=category)

    context = {
        "category":category,
        "products":products,
    }
    return render(request, "core/category-product-list.html", context)
def vendor_list_view(request):
    vendors = Vendor.objects.all()
    context = {
        "vendors": vendors,
    }
    return render(request, "core/vendor-list.html", context)
def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(vendor=vendor, product_status="published").order_by("-id")

    context = {
        "vendor": vendor,
        "products": products,
    }
    return render(request, "core/vendor-detail.html", context)

def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)
    # product = get_object_or_404(Product, pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)

    # Getting all reviews related to a product
    reviews = ProductReview.objects.filter(product=product).order_by("-date")

    # Getting average review
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    # Product Review form
    review_form = ProductReviewForm()
    make_review = True
    if request.user.is_authenticated:
        try:
            address = Address.objects.get(status=True, user=request.user)
        except Address.DoesNotExist:
            address = "Address not found"
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()

        if user_review_count > 0:
            make_review = False
    else:
        address = "Login To Continue"

    p_image = product.p_images.all()

    context = {
        "p": product,
        "address": address,
        "make_review": make_review,
        "review_form": review_form,
        "p_image": p_image,
        "average_rating": average_rating,
        "reviews": reviews,
        "products": products,
    }

    return render(request, "core/product-detail.html", context)


def tag_list(request, tag_slug=None):

    products = Product.objects.filter(product_status="published").order_by("-id")

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {
        "products": products,
        "tag": tag
    }

    return render(request, "core/tag.html", context)

def ajax_add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user

    review = ProductReview.objects.create(
        user=user,
        product=product,
        review = request.POST['review'],
        rating = request.POST['rating'],
    )

    context = {
        'user': user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return JsonResponse(
       {
         'bool': True,
        'context': context,
        'average_reviews': average_reviews
       }
    )
def search_view(request):
    query = request.GET.get("q")

    products = Product.objects.filter(title__icontains=query).order_by("-date")

    context = {
        "products": products,
        "query": query,
    }
    return render(request, "core/search.html", context)


def filter_product(request):
    categories = request.GET.getlist("category[]")
    vendors = request.GET.getlist("vendor[]")

    # Get price range, defaulting to a broad range if not specified
    min_price = request.GET.get('min_price', 10)
    max_price = request.GET.get('max_price', 999999)

    # Filter products
    products = Product.objects.filter(product_status="published").distinct()

    # Apply price filter
    products = products.filter(price__gte=min_price, price__lte=max_price)

    # Apply category filter
    if categories:
        products = products.filter(category__id__in=categories).distinct()

    # Apply vendor filter
    if vendors:
        products = products.filter(vendor__id__in=vendors).distinct()

    # Render the filtered products
    data = render_to_string("core/async/product-list.html", {"products": products})
    return JsonResponse({"data": data})



def add_to_cart(request):
    if request.method == "GET":
        product_id = request.GET.get("id")
        product_qty = float(request.GET.get("qty", 1))  # Default to 1 if not provided

        # Fetch product details from the database
        product = get_object_or_404(Product, id=product_id)

        # Build the cart product object
        cart_product = {
            str(product.id): {
                "title": product.title,
                  "qty": max(1, float(product_qty)),
                "price": float(product.price),  # Fetch price directly from the database
                "image": product.image.url,  # Get image URL
                "pid": product.id,
                "size": request.GET.get("size", "Medium"),  # Default size to "Medium" if not provided
            }
        }

        # Handle session cart data
        if "cart_data_obj" in request.session:
            cart_data = request.session["cart_data_obj"]

            if str(product.id) in cart_data:
                # Update quantity and size for an existing product
                cart_data[str(product.id)]["qty"] += product_qty
                cart_data[str(product.id)]["size"] = cart_product[str(product.id)]["size"]
            else:
                # Add new product to cart
                cart_data.update(cart_product)

            request.session["cart_data_obj"] = cart_data
        else:
            # Initialize session with the new product
            request.session["cart_data_obj"] = cart_product

        # Return updated cart data
        return JsonResponse({
            "data": request.session["cart_data_obj"],
            "totalcartitems": len(request.session["cart_data_obj"]),
        })

    return JsonResponse({"error": "Invalid request method"}, status=400)

def cart_view(request):
    cart_total_amount = 0

    # Check if cart data exists in the session
    if "cart_data_obj" in request.session:
        cart_data = request.session["cart_data_obj"]

        for p_id, item in cart_data.items():
            try:
                # Ensure `qty` and `price` are valid floats
                qty = float(item.get("qty", 0))  # Default to 0 if missing or invalid
                price = float(item.get("price", 0))  # Default to 0 if missing or invalid

                # Calculate subtotal and add to total amount
                item["subtotal"] = qty * price
                cart_total_amount += item["subtotal"]
            except (ValueError, TypeError):
                # Handle invalid `qty` or `price` gracefully
                item["subtotal"] = 0

        return render(request, "core/cart.html", {
            "cart_data": cart_data,
            "totalcartitems": len(cart_data),
            "cart_total_amount": cart_total_amount,
        })
    else:
        # Redirect to home if cart is empty
        messages.warning(request, "Your cart is empty.")
        return redirect("core:index")




def delete_item_from_cart(request):
    product_id = str(request.GET["id"])

    if "cart_data_obj" in request.session:
        cart_data = request.session["cart_data_obj"]

        # Remove the product if it exists in the cart
        if product_id in cart_data:
            del cart_data[product_id]
            request.session["cart_data_obj"] = cart_data

    # Calculate updated total amount and render updated cart list
    cart_total_amount = 0
    if "cart_data_obj" in request.session:
        for item in request.session["cart_data_obj"].values():
            item["subtotal"] = float(item["qty"]) * float(item["price"])
            cart_total_amount += item["subtotal"]

    context = render_to_string("core/async/cart-list.html", {
        "cart_data": request.session.get("cart_data_obj", {}),
        "totalcartitems": len(request.session.get("cart_data_obj", {})),
        "cart_total_amount": cart_total_amount,
    })
    return JsonResponse({"data": context, "totalcartitems": len(request.session.get("cart_data_obj", {}))})




def update_cart(request):
    product_id = str(request.GET["id"])
    product_qty = float(request.GET["qty"])  # Ensure qty is a float

    if "cart_data_obj" in request.session:
        cart_data = request.session["cart_data_obj"]

        # Update the quantity of the product in the cart
        if product_id in cart_data:
            cart_data[product_id]["qty"] = product_qty
            request.session["cart_data_obj"] = cart_data

    # Calculate updated total amount and render updated cart list
    cart_total_amount = 0
    if "cart_data_obj" in request.session:
        for item in request.session["cart_data_obj"].values():
            item["subtotal"] = float(item["qty"]) * float(item["price"])
            cart_total_amount += item["subtotal"]

    context = render_to_string("core/async/cart-list.html", {
        "cart_data": request.session.get("cart_data_obj", {}),
        "totalcartitems": len(request.session.get("cart_data_obj", {})),
        "cart_total_amount": cart_total_amount,
    })
    return JsonResponse({"data": context, "totalcartitems": len(request.session.get("cart_data_obj", {}))})




# views.py

def save_checkout_info(request, order=None):
    cart_total_amount = 0
    total_amount = 0

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Please login or register to continue with the checkout.")
            return redirect('userauths:sign-in')

        # Fetch data from POST request and store in session
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        country = request.POST.get("country")
        manager = request.POST.get("manager")
        location = request.POST.get("location")

        request.session['full_name'] = full_name
        request.session['email'] = email
        request.session['mobile'] = mobile
        request.session['address'] = address
        request.session['city'] = city
        request.session['state'] = state
        request.session['country'] = country
        request.session['manager'] = manager
        request.session['location'] = location

        if 'cart_data_obj' in request.session:
            for p_id, item in request.session['cart_data_obj'].items():
                total_amount += int(item['qty']) * float(item['price'])

            full_name = request.session['full_name']
            email = request.session['email']
            phone = request.session['mobile']
            address = request.session['address']
            city = request.session['city']
            state = request.session['state']
            country = request.session['country']
            manager = request.session['manager']
            location = request.session['location']

            order = CartOrder.objects.create(
                user=request.user,
                price=total_amount,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                state=state,
                country=country,
                manager=manager,
                location=location,
            )

            keys_to_delete = ['full_name', 'email', 'mobile', 'address', 'city', 'state', 'country', 'manager', 'location']
            for key in keys_to_delete:
                if key in request.session:
                    del request.session[key]

            for p_id, item in request.session['cart_data_obj'].items():
                cart_total_amount += int(item['qty']) * float(item['price'])

                # Include size in CartOrderProducts
                CartOrderProducts.objects.create(
                    order=order,
                    invoice_no="INVOICE_NO-" + str(order.id),
                    item=item['title'],
                    image=item['image'],
                    qty=item['qty'],
                    price=item['price'],
                    total=float(item['qty']) * float(item['price']),
                    size=item.get('size' , 'Medium')
                )
                print("Received size:", request.GET.get('size'))


            return redirect("core:checkout", order.oid)

        return redirect("core:checkout", order.oid)

    return redirect("core:checkout", order.oid)


@csrf_exempt
def create_checkout_session(request, oid):
    order = CartOrder.objects.get(oid=oid)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        customer_email = order.email,
        payment_method_types=['card'],
        line_items = [
            {
                'price_data': {
                    'currency': 'USD',
                    'product_data': {
                        'name': order.full_name
                    },
                    'unit_amount': int(order.price * 100)
                },
                'quantity': 1
            }
        ],
        mode = 'payment',
        success_url = request.build_absolute_uri(reverse("core:payment-completed", args=[order.oid])) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url = request.build_absolute_uri(reverse("core:payment-completed", args=[order.oid]))
    )

    order.paid_status = False
    order.stripe_payment_intent = checkout_session['id']
    order.save()

    print("checkkout session", checkout_session)
    return JsonResponse({"sessionId": checkout_session.id})


@login_required
def checkout(request, oid):
    # Retrieve the order and associated items
    order = CartOrder.objects.get(oid=oid)
    order_items = CartOrderProducts.objects.filter(order=order)
    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        # Apply coupon if code is provided
        code = request.POST.get("code")
        if code:
            coupon = Coupon.objects.filter(code=code, active=True).first()
            if coupon:
                if coupon in order.coupons.all():
                    messages.warning(request, "Coupon already activated")
                else:
                    discount = coupon.discount
                    order.coupons.add(coupon)
                    order.price -= discount
                    order.saved += discount
                    order.save()

                    messages.success(request, "Coupon Activated")
            else:
                messages.error(request, "Coupon Does Not Exist")
            return redirect("core:checkout", oid=order.oid)

        # Handle wallet payment
        use_wallet = request.POST.get("use_wallet")
        if use_wallet:
            if profile.allocated_funds >= order.price:
                # Deduct the order price from the wallet
                profile.allocated_funds -= order.price
                profile.save()

                # Mark order as paid
                order.status = 'paid'  # Set the order status as 'paid'
                order.paid_status = True  # Ensure the paid status is updated
                order.save()

                # Clear the cart session after successful payment
                if 'cart_data_obj' in request.session:
                    del request.session['cart_data_obj']

                # Send a payment confirmation email (similar to the pay later logic)
                email_context = {
                    "user": request.user,
                    "order": order,
                    "order_items": order_items,
                    "total_sum": sum([item.total for item in order_items]),
                }
                email_message = render_to_string('core/order_confirmation.html', email_context)

                send_mail(
                    subject=f"Order Confirmation - INV-{order.id}",
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    html_message=email_message,
                )

                # Notify yourself of the new order
                send_mail(
                    subject=f"New Order Placed - {request.user.username}",
                    message=f"Customer {request.user.username} ({request.user.email}) has placed an order. Please check.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['alvotheboss@gmail.com'],  # or use [settings.DEFAULT_FROM_EMAIL]
                )

                messages.success(request, "Your payment has been completed using your wallet, and your cart has been cleared.")
                return redirect('core:payment-completed', oid=order.oid)  # Redirect to payment completed page with order ID
            else:
                messages.error(request, "Insufficient wallet balance to complete the purchase.")
                return redirect('core:checkout', oid=order.oid)

    context = {
        "order": order,
        "order_items": order_items,
        "wallet_balance": profile.allocated_funds,  # Pass wallet balance to the template
        "stripe_publishable_key": settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, "core/checkout.html", context)

@login_required
def payment_completed_view(request, oid):
    # Retrieve the order using the order ID
    order = CartOrder.objects.get(oid=oid)

    if not order.paid_status:  # Check if the order is not already paid
        order.paid_status = True  # Update the paid status
        order.save()

    context = {
        "order": order,
        "stripe_publishable_key": settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'core/payment-completed.html', context)

@login_required
def payment_failed_view(request):
    return render(request, 'core/payment-failed.html')


@login_required
def customer_dashboard(request):
    # Get user's orders and addresses
    orders_list = CartOrder.objects.filter(user=request.user).order_by("-id")
    address = Address.objects.filter(user=request.user)

    # Aggregate orders by month
    orders = (
        CartOrder.objects
        .filter(user=request.user)
        .annotate(month=ExtractMonth("order_date"))
        .values("month")
        .annotate(count=Count("id"))
        .values("month", "count")
    )

    month = []
    total_orders = []

    for i in orders:
        month.append(calendar.month_name[i["month"]])
        total_orders.append(i["count"])

    # Handle address addition and account updates
    if request.method == "POST":
        if "submit_address" in request.POST:  # Address submission
            address_text = request.POST.get("address")
            mobile = request.POST.get("mobile")

            if address_text and mobile:  # Basic validation
                Address.objects.create(
                    user=request.user,
                    address=address_text,
                    mobile=mobile,
                )
                messages.success(request, "Address Added Successfully.")
                return redirect("core:dashboard")
            else:
                messages.error(request, "Please fill in all fields.")

        elif "submit_account" in request.POST:  # Account details submission
            first_name = request.POST.get("name")
            last_name = request.POST.get("phone")
            display_name = request.POST.get("dname")
            email = request.POST.get("email")
            current_password = request.POST.get("password")
            new_password = request.POST.get("npassword")
            confirm_password = request.POST.get("cpassword")

            # Check if current password is correct
            if check_password(current_password, request.user.password):
                if new_password == confirm_password:
                    # Update user profile
                    user_profile = Profile.objects.get(user=request.user)
                    user_profile.first_name = first_name
                    user_profile.last_name = last_name
                    user_profile.display_name = display_name
                    user_profile.email = email
                    user_profile.save()

                    # Change the user's password
                    request.user.set_password(new_password)
                    request.user.save()

                    # Update the session to avoid logout
                    update_session_auth_hash(request, request.user)

                    messages.success(request, "Account details updated successfully.")
                    return redirect("core:dashboard")
                else:
                    messages.error(request, "New passwords do not match.")
            else:
                messages.error(request, "Current password is incorrect.")

    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect("userauths:profile-create")  # Redirect to profile creation or another suitable page

    context = {
        "user_profile": user_profile,
        "orders": orders,
        "orders_list": orders_list,
        "address": address,
        "month": month,
        "total_orders": total_orders,
    }

    return render(request, 'core/dashboard.html', context)

def make_address_default(request):
    id = request.GET['id']
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean": True})

@login_required
def wishlist_view(request):
    wishlist = wishlist_model.objects.all()
    context = {
        "w":wishlist
    }
    return render(request, "core/wishlist.html", context)

def add_to_wishlist(request):
    product_id = request.GET['id']
    product = Product.objects.get(id=product_id)
    print("product id isssssssssssss:" + product_id)

    context = {}

    wishlist_count = wishlist_model.objects.filter(product=product, user=request.user).count()
    print(wishlist_count)

    if wishlist_count > 0:
        context = {
            "bool": True
        }
    else:
        new_wishlist = wishlist_model.objects.create(
            user=request.user,
            product=product,
        )
        context = {
            "bool": True
        }

    return JsonResponse(context)

def remove_wishlist(request):
    pid = request.GET['id']
    wishlist = wishlist_model.objects.filter(user=request.user)
    wishlist_d = wishlist_model.objects.get(id=pid)
    delete_product = wishlist_d.delete()

    context = {
        "bool":True,
        "w":wishlist
    }
    wishlist_json = serializers.serialize('json', wishlist)
    t = render_to_string('core/async/wishlist-list.html', context)
    return JsonResponse({'data':t,'w':wishlist_json})

# Other Pages
def contact(request):
    return render(request, "core/contact.html")


def ajax_contact_form(request):
    full_name = request.GET['full_name']
    email = request.GET['email']
    phone = request.GET['phone']
    subject = request.GET['subject']
    message = request.GET['message']

    contact = ContactUs.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
        subject=subject,
        message=message,
    )

    data = {
        "bool": True,
        "message": "Message Sent Successfully"
    }

    return JsonResponse({"data":data})

@login_required
def home_view(request):
    current_year = datetime.datetime.now().year
    return render(request, 'core/home.html', {'current_year': current_year})

def about_us(request):
    return render(request, "core/about_us.html")

def purchase_guide(request):
    return render(request, "core/purchase_guide.html")

def privacy_policy(request):
    return render(request, "core/privacy_policy.html")

def terms_of_service(request):
    return render(request, "core/terms_of_service.html")

def blog_view(request):
    return render(request, 'core/blog.html')


