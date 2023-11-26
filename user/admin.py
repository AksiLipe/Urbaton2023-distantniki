from django.contrib import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
    model = User


admin.site.register(User, UserAdmin)
admin.site.register(News)
admin.site.register(Municipality)
admin.site.register(City)
admin.site.register(Position)
admin.site.register(Appeal)
admin.site.register(Answer)
admin.site.register(Photo)
