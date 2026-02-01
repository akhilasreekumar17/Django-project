'''
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/', views.book_table, name='book_table'),
    
    path('register/', views.register, name='register'),
    path('order/', views.order_food, name='order_food'),
    path('booking-success/', views.booking_success, name='booking_success'), 
    path('logout/', views.user_logout, name='logout'),
    path('login/', views.user_login, name='login'), 
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-login/', views.admin_login, name='admin_login'),
    
    # Booking Management
    path('approve-booking/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('reject-booking/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    
    # Food Management
    path('add-food/', views.add_food_item, name='add_food_item'),
    path('edit-food/<int:food_id>/', views.edit_food_item, name='edit_food_item'),
    path('delete-food/<int:food_id>/', views.delete_food_item, name='delete_food_item'),
    
    # Cart Management
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:cart_item_id>/', views.update_cart, name='update_cart'),
    
    # Order Management
    path('checkout/', views.checkout, name='checkout'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    
    # Admin Order Management
    path('admin-orders/', views.admin_orders, name='admin_orders'),
    path('confirm-order/<int:order_id>/', views.confirm_order, name='confirm_order'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
]
'''
from django.urls import path
from . import views

urlpatterns = [

    # -------------------- PUBLIC / USER --------------------
    path('', views.home, name='home'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('admin-login/', views.admin_login, name='admin_login'),

    # -------------------- TABLE BOOKING --------------------
    path('book/', views.book_table, name='book_table'),
    path(
        'booking-success/<int:booking_id>/',
        views.booking_success,
        name='booking_success'
    ),

    # -------------------- FOOD ORDERING --------------------
    path('order/', views.order_food, name='order_food'),

    # -------------------- CART --------------------
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('update-cart/<int:cart_item_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # -------------------- CHECKOUT & ORDERS --------------------
    path('checkout/', views.checkout, name='checkout'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),

    # User Orders (VIEW ONLY)
    path('my-orders/', views.my_orders, name='my_orders'),

    # -------------------- ADMIN DASHBOARD --------------------
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    

    # Food Management (ADMIN)
    path('add-food/', views.add_food_item, name='add_food_item'),
    path('edit-food/<int:food_id>/', views.edit_food_item, name='edit_food_item'),
    path('delete-food/<int:food_id>/', views.delete_food_item, name='delete_food_item'),
    path("admin-foods/", views.admin_food_list, name="admin_food_list"),


    # -------------------- ADMIN ORDER MANAGEMENT --------------------
    path('admin-orders/', views.admin_orders, name='admin_orders'),

    # Order Status Transitions (ADMIN ONLY)
    path('confirm-order/<int:order_id>/', views.confirm_order, name='confirm_order'),
    path('mark-ready/<int:order_id>/', views.mark_order_ready, name='mark_order_ready'),
    path('complete-order/<int:order_id>/', views.complete_order, name='complete_order'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),

    # -------------------- NOTIFICATIONS --------------------
    path('notifications/', views.notifications, name='notifications'),
    path(
        'mark-notification-read/<int:notification_id>/',
        views.mark_notification_read,
        name='mark_notification_read'
    ),

    # Admin Order Status Updates
    path('order-ready/<int:order_id>/', views.mark_order_ready, name='mark_order_ready'),
    path('order-complete/<int:order_id>/', views.complete_order, name='complete_order'),
    #Password Reset
    path('forgot-password/', views.forgot_password_verify, name='forgot_password'),
    path('set-new-password/', views.set_new_password, name='set_new_password'),

    # -------------------- TABLE BOOKING MANAGEMENT --------------------
    path("admin-tables/", views.admin_tables, name="admin_tables"),
    path("admin-tables/add/", views.add_table, name="add_table"),
    path("admin-tables/edit/<int:table_id>/", views.edit_table, name="edit_table"),
    path(
    'table-review/<int:table_id>/',
    views.add_table_review,
    name='add_table_review'
),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('table/<int:table_id>/', views.table_detail, name='table_detail'),


]
