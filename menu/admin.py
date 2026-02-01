from django.contrib import admin
from .models import (
    Category,
    FoodItem,
    Table,
    TableBooking,
    TableReview,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Notification,
)

# =========================
# CATEGORY
# =========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


# =========================
# FOOD ITEM
# =========================
@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "price",
        "available",
    )
    list_filter = ("category", "available")
    search_fields = ("name", "description")
    list_editable = ("price", "available")
    ordering = ("name",)


# =========================
# TABLE (ADMIN CONTROLLED)
# =========================
@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = (
        "table_number",
        "seats",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "seats")
    search_fields = ("table_number", "description")
    list_editable = ("seats", "is_active")
    ordering = ("table_number",)
    readonly_fields = ("created_at",)

    fieldsets = (
        ("🪑 Table Info", {
            "fields": (
                "table_number",
                "seats",
                "description",
                "image",
            )
        }),
        ("⚙️ Status", {
            "fields": ("is_active",)
        }),
        ("⏱ Meta", {
            "fields": ("created_at",)
        }),
    )


# =========================
# TABLE BOOKING (AUTO CONFIRM)
# =========================
@admin.register(TableBooking)
class TableBookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "table",
        "date",
        "time",
        "created_at",
    )
    list_filter = ("date", "table")
    search_fields = (
        "user__username",
        "table__table_number",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)


# =========================
# TABLE REVIEW
# =========================
@admin.register(TableReview)
class TableReviewAdmin(admin.ModelAdmin):
    list_display = (
        "table",
        "user",
        "rating",
        "created_at",
    )
    list_filter = ("rating", "created_at")
    search_fields = (
        "table__table_number",
        "user__username",
        "comment",
    )
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


# =========================
# CART
# =========================
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "updated_at")
    search_fields = ("user__username",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-updated_at",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "food", "quantity", "added_at")
    list_filter = ("added_at",)
    search_fields = ("cart__user__username", "food__name")
    readonly_fields = ("added_at",)
    ordering = ("-added_at",)


# =========================
# ORDER
# =========================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "final_amount",
        "payment_method",
        "payment_status",
        "order_status",
        "created_at",
    )
    list_filter = (
        "order_status",
        "payment_status",
        "created_at",
    )
    search_fields = (
        "order_number",
        "user__username",
    )
    ordering = ("-created_at",)

    readonly_fields = (
        "order_number",
        "user",
        "total_amount",
        "delivery_charge",
        "final_amount",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("📦 Order Info", {
            "fields": (
                "order_number",
                "user",
                "created_at",
                "updated_at",
            )
        }),
        ("💰 Amounts", {
            "fields": (
                "total_amount",
                "delivery_charge",
                "final_amount",
            )
        }),
        ("💳 Payment", {
            "fields": (
                "payment_method",
                "payment_status",
            )
        }),
        ("📊 Status", {
            "fields": (
                "order_status",
                "estimated_time",
            )
        }),
        ("📝 Instructions", {
            "fields": ("special_instructions",)
        }),
    )


# =========================
# ORDER ITEM
# =========================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "food",
        "quantity",
        "price",
        "subtotal",
    )
    list_filter = ("order__created_at",)
    search_fields = ("order__order_number", "food__name")
    readonly_fields = (
        "order",
        "food",
        "quantity",
        "price",
        "subtotal",
    )
    ordering = ("-order__created_at",)


# =========================
# NOTIFICATION
# =========================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "notification_type",
        "is_read",
        "created_at",
    )
    list_filter = (
        "notification_type",
        "is_read",
        "created_at",
    )
    search_fields = (
        "title",
        "message",
        "user__username",
    )
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
