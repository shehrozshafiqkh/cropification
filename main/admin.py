from django.contrib import admin

# Register your models here.
from .models import *
# Register your models here.

admin.site.register(User)
admin.site.register(pics)
admin.site.register(contact)
admin.site.register(history)
admin.site.register(newsalert)