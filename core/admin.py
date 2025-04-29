from django.contrib import admin
from core.models import (
    CartOrderProducts, Coupon, Product, Category, Vendor,
    CartOrder, ProductImages, ProductReview, wishlist_model, Address
)

# Inline for Product Images in Product Admin
class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages

# Product Admin
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_editable = ['title', 'price', 'featured', 'product_status']
    list_display = ['user', 'title', 'product_image', 'price', 'category', 'vendor', 'featured', 'product_status', 'pid']

# Category Admin
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image']

# Vendor Admin
class VendorAdmin(admin.ModelAdmin):
    list_display = ['title', 'vendor_image']

# CartOrder Admin with manager and location display
class CartOrderAdmin(admin.ModelAdmin):
    list_editable = ['paid_status', 'product_status', 'sku']
    list_display = ['user', 'price', 'paid_status', 'order_date', 'product_status', 'sku', 'manager', 'location']

    def manager(self, obj):
        # Retrieves manager from related Profile model if exists
        return getattr(obj.user.profile, 'manager', None)
    manager.short_description = 'Manager'

    def location(self, obj):
        # Retrieves location from related Profile model if exists
        return getattr(obj.user.profile, 'location', None)
    location.short_description = 'Location'

# CartOrderProducts Admin
class CartOrderProductsAdmin(admin.ModelAdmin):
    list_display = ['order', 'invoice_no', 'item', 'image', 'qty', 'price', 'total']

# ProductReview Admin
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'review', 'rating']

# Wishlist Admin
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'date']

# Address Admin
class AddressAdmin(admin.ModelAdmin):
    list_editable = ['address', 'status']
    list_display = ['user', 'address', 'status']

# Helper function to register models safely
def register_model(model, model_admin=None):
    try:
        admin.site.register(model, model_admin)
    except admin.sites.AlreadyRegistered:
        pass

# Register models with the admin site
register_model(Product, ProductAdmin)
register_model(Category, CategoryAdmin)
register_model(Vendor, VendorAdmin)
register_model(CartOrder, CartOrderAdmin)
register_model(CartOrderProducts, CartOrderProductsAdmin)
register_model(ProductReview, ProductReviewAdmin)
register_model(wishlist_model, WishlistAdmin)
register_model(Address, AddressAdmin)
register_model(Coupon)
