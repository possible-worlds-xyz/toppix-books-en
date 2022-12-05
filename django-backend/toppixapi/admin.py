from django.contrib import admin
from .models import Book, Country, Character, Continent, Country, Time

# Register your models here.

admin.site.register(Book)
admin.site.register(Character)
admin.site.register(Continent)
admin.site.register(Country)
admin.site.register(Time)
