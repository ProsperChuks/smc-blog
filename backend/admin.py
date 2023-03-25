from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib import admin
from .models import *

class UserCreationFormExtended(UserCreationForm): 
    class Meta:
        model = User
        fields = ['email', 'name', 'slug']

UserAdmin.add_form = UserCreationFormExtended
UserAdmin.add_fieldsets = (
    (None, {
        'fields': ('email', 'name', 'username', 'slug', 'password1', 'password2',)
    }),
)

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(category,)
admin.site.register(post)
admin.site.register(postReview)
admin.site.register(subscribedUsers)
admin.site.register(comment)
