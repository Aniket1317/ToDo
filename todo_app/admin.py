from django.contrib import admin
from .models import Todo
# Register your models here.

class TodoAdmin(admin.ModelAdmin):
	readonly_fields = ('time',)

admin.site.register(Todo,TodoAdmin)
