# home/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

# Use the configured user model (usually 'auth.User')
User = settings.AUTH_USER_MODEL


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — ₹{self.price}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    order_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-order_date"]

    def __str__(self):
        # user may be a string when using AUTH_USER_MODEL; this is safe
        return f"Order #{self.id} by {self.user}"

    @property
    def total_amount(self):
        # Sum of item price * quantity
        return sum(item.line_total for item in self.items.select_related("product").all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("order", "product")

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def line_total(self):
        return self.product.price * self.quantity
