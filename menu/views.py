from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .models import Table
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta


from .models import Order, Notification  # Ensure Notification is imported
from .models import (
    FoodItem, Category,
    Table, TableBooking, TableReview,
    Cart, CartItem,
    Order, OrderItem,
    Notification
)

from .forms import FoodItemForm
import random
import string


# ========================= HOME =========================

def home(request):
    foods = FoodItem.objects.filter(available=True)
    return render(request, "menu/home.html", {"foods": foods})


# ========================= AUTH =========================

def register(request):
    if request.method == "POST":
        if User.objects.filter(username=request.POST["username"]).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(
            username=request.POST["username"],
            email=request.POST["email"],
            password=request.POST["password"]
        )
        user.first_name = request.POST.get("full_name", "")
        user.save()

        messages.success(request, "Registration successful. Please login.")
        return redirect("login")

    return render(request, "registration/register.html")


def user_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if not user:
            messages.error(request, "Invalid username or password")
            return redirect("login")

        if user.is_staff:
            messages.error(request, "Admins must login from Admin Login page")
            return redirect("login")

        login(request, user)
        return redirect("home")

    return render(request, "registration/login.html")


def admin_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if user and user.is_staff:
            login(request, user)
            return redirect("admin_dashboard")

        messages.error(request, "Invalid admin credentials")
        return redirect("admin_login")

    return render(request, "registration/admin_login.html")
def forgot_password_verify(request):
    if request.method == "POST":
        username = request.POST.get('username')
        name = request.POST.get('name')

        # Checking if user exists with matching username and first_name
        # Note: You can change 'first_name' to 'last_name' depending on your registration logic
        user = User.objects.filter(username=username, first_name=name).first()

        if user:
            request.session['reset_user_id'] = user.id  # Store ID in session for the next step
            return redirect('set_new_password')
        else:
            messages.error(request, "Username and Name do not match.")
            
    return render(request, "registration/forgot_password_verify.html")

def set_new_password(request):
    # Security check: if they didn't come from the verify page, kick them back
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('forgot_password_verify')

    if request.method == "POST":
        new_pass = request.POST.get('password')
        confirm_pass = request.POST.get('confirm_password')

        if new_pass == confirm_pass:
            user = User.objects.get(id=user_id)
            user.set_password(new_pass) # This hashes the password automatically
            user.save()
            
            # Clean up session and redirect
            del request.session['reset_user_id']
            messages.success(request, "Password updated successfully!")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, "registration/set_new_password.html")

@require_POST
def user_logout(request):
    logout(request)
    return redirect("home")


# ========================= TABLE LIST & BOOKING =========================

from datetime import datetime, timedelta
from django.utils.timezone import now

@login_required
def book_table(request):
    tables = Table.objects.filter(is_active=True)

    if request.method == "POST":
        table_id = request.POST.get("table")
        date_str = request.POST.get("date")
        time_str = request.POST.get("time")

        # Basic Validation
        if not all([table_id, date_str, time_str]):
            messages.error(request, "❌ Please fill all fields.")
            return redirect("book_table")

        # 1. Convert to Python objects
        requested_dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        booking_date = requested_dt.date()
        booking_time = requested_dt.time()

        # 2. Prevent booking in the past
        if booking_date < now().date():
            messages.error(request, "❌ You cannot book for a past date.")
            return redirect("book_table")

        # 3. Buffer calculation (29 minutes ensures a 30-minute gap)
        start_buffer = (requested_dt - timedelta(minutes=29)).time()
        end_buffer = (requested_dt + timedelta(minutes=29)).time()

        # 4. Conflict Check
        conflict = TableBooking.objects.filter(
            table_id=table_id,
            date=date_str,
            time__range=(start_buffer, end_buffer)
        ).exists()

        if conflict:
            messages.error(
                request, 
                "❌ This table is already reserved within 30 minutes of your chosen time."
            )
            return redirect("book_table")

        # 5. Create the booking using the correct variables
        booking = TableBooking.objects.create(
            user=request.user,
            table_id=table_id,
            date=booking_date,
            time=booking_time
        )

        messages.success(request, "✅ Booking confirmed!")
        return redirect("booking_success", booking_id=booking.id)

    return render(request, "menu/booking.html", {"tables": tables})

@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(
        TableBooking,
        id=booking_id,
        user=request.user
    )

    return render(request, "menu/booking_success.html", {
        "booking": booking
    })
from datetime import datetime, timedelta
from django.utils import timezone

@login_required
def table_detail(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    
    if request.method == "POST":
        date_str = request.POST.get("date")
        time_str = request.POST.get("time")

        # 1. Parse into a single datetime object
        try:
            requested_dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        except ValueError:
            messages.error(request, "❌ Invalid date or time format.")
            return redirect("table_detail", table_id=table.id)
        
        # 2. Prevent Past Bookings (Using timezone-aware comparison)
        if requested_dt < datetime.now():
            messages.error(request, "❌ You cannot book a table for a past date or time.")
            return redirect("table_detail", table_id=table.id)

        # 3. 30-Minute Buffer Check
        start_range = (requested_dt - timedelta(minutes=29)).time()
        end_range = (requested_dt + timedelta(minutes=29)).time()

        conflict = TableBooking.objects.filter(
            table=table,
            date=date_str,
            time__range=(start_range, end_range)
        ).exists()

        if conflict:
            messages.error(request, "❌ This table is already booked within 30 minutes of your requested time.")
            return redirect("table_detail", table_id=table.id)

        # 4. Save Booking (Assigned to variable to fix NameError)
        new_booking = TableBooking.objects.create(
            user=request.user,
            table=table,
            date=requested_dt.date(),
            time=requested_dt.time()
        )
        
        messages.success(request, "✅ Table booked successfully!")
        return redirect("booking_success", booking_id=new_booking.id)

    return render(request, "menu/table_detail.html", {
        "table": table,
        "reviews": table.reviews.all()
    })
@login_required
def my_bookings(request):
    # Fetch bookings for the logged-in user
    bookings = TableBooking.objects.filter(user=request.user).order_by('-date')
    return render(request, 'menu/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(TableBooking, id=booking_id, user=request.user)
    if request.method == 'POST':
        # Instead of deleting, we update a status (if your model has a status field)
        # If you haven't added a status field yet, delete() is fine, but
        # usually, we keep the record and mark it 'Cancelled'.
        booking.delete() 
        messages.success(request, f"Table {booking.table.table_number} booking has been cancelled.")
        return redirect('my_bookings')
    return redirect('my_bookings')
# ========================= TABLE REVIEWS =========================

@login_required
def add_table_review(request, table_id):
    table = get_object_or_404(Table, id=table_id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        TableReview.objects.update_or_create(
            table=table,
            user=request.user,
            defaults={
                "rating": rating,
                "comment": comment
            }
        )

        messages.success(request, "⭐ Thank you for your review!")
        return redirect("book_table")

    return render(request, "menu/add_review.html", {
        "table": table
    })


# ========================= FOOD ORDER =========================

@login_required
def order_food(request):
    return render(request, "menu/order_food.html", {
        "foods": FoodItem.objects.filter(available=True),
        "categories": Category.objects.all()
    })


# ========================= ADMIN DASHBOARD =========================

@staff_member_required(login_url="admin_login")
def admin_dashboard(request):
    return render(request, "menu/admin_dashboard.html")


# ========================= ADMIN – FOOD =========================

@staff_member_required(login_url="admin_login")
def add_food_item(request):
    form = FoodItemForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Food item added")
        return redirect("admin_dashboard")
    return render(request, "menu/add_food_item.html", {"form": form})


@staff_member_required(login_url="admin_login")
def edit_food_item(request, food_id):
    food = get_object_or_404(FoodItem, id=food_id)
    form = FoodItemForm(request.POST or None, request.FILES or None, instance=food)
    if form.is_valid():
        form.save()
        messages.success(request, "Food updated")
        return redirect("admin_dashboard")
    return render(request, "menu/edit_food_item.html", {"form": form})

@staff_member_required(login_url="admin_login")
def admin_food_list(request):
    foods = FoodItem.objects.select_related("category").all()
    categories = Category.objects.all()

    return render(request, "menu/admin_food_list.html", {
        "foods": foods,
        "categories": categories
    })
@staff_member_required(login_url="admin_login")
def delete_food_item(request, food_id):
    food = get_object_or_404(FoodItem, id=food_id)
    food.delete()
    messages.success(request, "Food deleted")
    return redirect("admin_dashboard")
# ========================= ADMIN TABLE MANAGEMENT =========================


@staff_member_required
def admin_tables(request):
    tables = Table.objects.prefetch_related("bookings", "bookings__user")
    return render(request, "menu/admin_tables.html", {
        "tables": tables,
        "today": now().date()
    })

@staff_member_required(login_url="admin_login")
def add_table(request):
    if request.method == "POST":
        Table.objects.create(
            table_number=request.POST["table_number"],
            seats=request.POST["seats"],
            description=request.POST.get("description", ""),
            image=request.FILES.get("image"),
            is_active=True
        )
        messages.success(request, "✅ Table added successfully")
        return redirect("admin_tables")

    return render(request, "menu/add_table.html")


@staff_member_required(login_url="admin_login")
def edit_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)

    if request.method == "POST":
        table.table_number = request.POST["table_number"]
        table.seats = request.POST["seats"]
        table.description = request.POST.get("description", "")
        table.is_active = "is_active" in request.POST

        if request.FILES.get("image"):
            table.image = request.FILES["image"]

        table.save()
        messages.success(request, "✅ Table updated")
        return redirect("admin_tables")

    return render(request, "menu/edit_table.html", {
        "table": table
    })

# ========================= CART =========================

@login_required
def add_to_cart(request, food_id):
    food = get_object_or_404(FoodItem, id=food_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, food=food)

    if not created:
        item.quantity += 1
        item.save()

    messages.success(request, "Added to cart")
    return redirect("view_cart")


@login_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    items = cart.cartitem_set.all() if cart else []

    return render(request, "menu/view_cart.html", {
        "cart_items": items,
        "total": cart.get_total() if cart else 0
    })


@login_required
@require_POST
def remove_from_cart(request, cart_item_id):
    CartItem.objects.filter(
        id=cart_item_id,
        cart__user=request.user
    ).delete()
    messages.success(request, "Item removed")
    return redirect("view_cart")


@login_required
def update_cart(request, cart_item_id):
    cart_item = get_object_or_404(
        CartItem,
        id=cart_item_id,
        cart__user=request.user
    )

    quantity = int(request.POST.get("quantity", 1))

    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    return redirect("view_cart")


# ========================= CHECKOUT & ORDERS =========================

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = CartItem.objects.filter(cart=cart)
    subtotal = sum(i.get_subtotal() for i in items)

    return render(request, "menu/checkout.html", {
        "cart_items": items,
        "subtotal": subtotal,
        "final_amount": subtotal 
    })


@login_required
def process_payment(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = CartItem.objects.filter(cart=cart)

    order = Order.objects.create(
        user=request.user,
        order_number="ORD" + "".join(random.choices(string.digits, k=8)),
        total_amount=sum(i.get_subtotal() for i in items),
        final_amount=sum(i.get_subtotal() for i in items) ,
        payment_method=request.POST["payment_method"],
        payment_status="Pending",
        order_status="Pending"
    )

    for i in items:
        OrderItem.objects.create(
            order=order,
            food=i.food,
            quantity=i.quantity,
            price=i.food.price,
            subtotal=i.get_subtotal()
        )

    items.delete()
    messages.success(request, "Order placed successfully")
    return redirect("order_success", order_id=order.id)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "menu/order_success.html", {
        "order": order,
        "order_items": OrderItem.objects.filter(order=order)
    })


@login_required
def my_orders(request):
    return render(request, "menu/my_orders.html", {
        "orders": Order.objects.filter(user=request.user)
    })


# ========================= ADMIN ORDER FLOW =========================



@staff_member_required(login_url="admin_login")
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at') # Added ordering for better UI
    return render(request, "menu/admin_orders.html", {
        "orders": orders,
        "all_count": orders.count(),
        "pending_count": orders.filter(order_status="Pending").count(),
        "confirmed_count": orders.filter(order_status="Confirmed").count(),
        "ready_count": orders.filter(order_status="Ready").count(),
        "completed_count": orders.filter(order_status="Completed").count(),
    })

@staff_member_required(login_url="admin_login")
@require_POST
def confirm_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.order_status = "Confirmed"
    est_time = request.POST.get("estimated_time", "20 minutes")
    order.estimated_time = est_time
    order.seen_by_user = False
    order.save()

    # CREATE NOTIFICATION
    Notification.objects.create(
        user=order.user,
        notification_type='order',
        title="Order Confirmed! ✅",
        message=f"Your order #{order.id} has been confirmed. Estimated time: {est_time}.",
        order=order
    )
    return redirect("admin_orders")

@staff_member_required(login_url="admin_login")
@require_POST
def mark_order_ready(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.order_status = "Ready"
    order.seen_by_user = False
    order.save()

    # CREATE NOTIFICATION
    Notification.objects.create(
        user=order.user,
        notification_type='order',
        title="Order Ready! 🍕",
        message=f"Great news! Your order #{order.id} is ready for pickup or delivery.",
        order=order
    )
    return redirect("admin_orders")

@staff_member_required(login_url="admin_login")
@require_POST
def complete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.order_status = "Completed"
    order.seen_by_user = False
    order.save()

    # CREATE NOTIFICATION
    Notification.objects.create(
        user=order.user,
        notification_type='order',
        title="Order Completed! ✨",
        message=f"Order #{order.id} has been marked as completed. Hope you enjoy your meal!",
        order=order
    )
    return redirect("admin_orders")

@staff_member_required(login_url="admin_login")
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.order_status = "Cancelled"
    order.seen_by_user = False
    order.save()

    # CREATE NOTIFICATION
    Notification.objects.create(
        user=order.user,
        notification_type='order',
        title="Order Cancelled ❌",
        message=f"We regret to inform you that your order #{order.id} has been cancelled.",
        order=order
    )
    return redirect("admin_orders")


# ========================= NOTIFICATIONS =========================

@login_required
def notifications(request):
    notifs = Notification.objects.filter(user=request.user)
    return render(request, "menu/notifications.html", {
        "notifications": notifs,
        "unread_count": notifs.filter(is_read=False).count()
    })


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    notif = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notif.is_read = True
    notif.save()
    return redirect("notifications")
