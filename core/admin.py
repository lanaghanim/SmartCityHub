from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Category,
    Department,
    Event,
    EventRegistration,
    Notification,
    ServiceRequest,
    User,
)


class SmartCityUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('SmartCity Hub', {'fields': ('role', 'phone_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('SmartCity Hub', {'fields': ('role', 'phone_number')}),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = UserAdmin.list_filter + ('role',)


admin.site.register(User, SmartCityUserAdmin)
admin.site.register(Category)
admin.site.register(Department)
admin.site.register(Event)
admin.site.register(ServiceRequest)
admin.site.register(Notification)
admin.site.register(EventRegistration)
