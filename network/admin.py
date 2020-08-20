from django.contrib import admin

# Register your models here.
from .models import Post, User, Like


class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("following",)


admin.site.register(Post)
admin.site.register(User, UserAdmin)
admin.site.register(Like)