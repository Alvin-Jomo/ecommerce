from django.contrib import admin
from userauths.models import User, ContactUs, Profile

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'is_approved')
    list_editable = ('is_active', 'is_approved')
    list_filter = ('is_active', 'is_approved')
    search_fields = ('username', 'email')

class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'subject']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'bio', 'phone', 'allocated_funds', 'location', 'manager']
    list_editable = ['allocated_funds', 'location', 'manager']  # Make fields editable in the list view
    fields = ['user', 'full_name', 'bio', 'phone', 'allocated_funds', 'location', 'manager']

admin.site.register(User, UserAdmin)
admin.site.register(ContactUs, ContactUsAdmin)
admin.site.register(Profile, ProfileAdmin)
