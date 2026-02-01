from django.db import models
from django.contrib.auth.models import User


# =========================
# CATEGORY & FOOD
# =========================
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# =========================
# CART
# =========================
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"

    def get_total(self):
        return sum(item.get_subtotal() for item in self.cartitem_set.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.food.name}"

    def get_subtotal(self):
        return self.quantity * self.food.price


# =========================
# ORDER
# =========================
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending - Waiting for Admin Confirmation'),
        ('Confirmed', 'Confirmed - Being Prepared'),
        ('Ready', 'Ready - Pick Up Available'),
        ('Completed', 'Completed - Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)

    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=6, decimal_places=2, default=50.00)
    final_amount = models.DecimalField(max_digits=8, decimal_places=2)

    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('UPI', 'UPI Payment'),
            ('Card', 'Credit/Debit Card'),
            ('NetBanking', 'Net Banking'),
            ('Wallet', 'Digital Wallet'),
            ('COD', 'Cash on Delivery'),
        ]
    )

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Completed', 'Completed'),
            ('Failed', 'Failed'),
        ],
        default='Pending'
    )

    order_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    estimated_time = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="e.g., 20 minutes"
    )

    special_instructions = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    seen_by_user = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.food.name} in Order #{self.order.order_number}"


# =========================
# TABLE (ADMIN CONTROLLED)
# =========================
class Table(models.Model):
    table_number = models.CharField(max_length=10, unique=True)
    seats = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="table_images/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["table_number"]

    def __str__(self):
        return f"Table {self.table_number} ({self.seats} seats)"

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(
                sum(review.rating for review in reviews) / reviews.count(),
                1
            )
        return 0

    @property
    def total_reviews(self):
        return self.reviews.count()



# =========================
# TABLE BOOKING (AUTO CONFIRM)
# =========================
class TableBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name="bookings")

    date = models.DateField()
    time = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('table', 'date', 'time')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - Table {self.table.table_number} on {self.date} {self.time}"


# =========================
# TABLE REVIEW
# =========================
class TableReview(models.Model):
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)]
    )
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('table', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Table {self.table.table_number} - {self.rating}⭐ by {self.user.username}"


# =========================
# NOTIFICATIONS
# =========================
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('order', 'Order Update'),
        ('booking', 'Booking Update'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    booking = models.ForeignKey(
        TableBooking,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"
