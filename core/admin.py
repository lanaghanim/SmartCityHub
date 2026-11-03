from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Event, ServiceRequest, Notification

admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Event)
admin.site.register(ServiceRequest)
admin.site.register(Notification)