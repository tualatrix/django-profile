from django.contrib import admin
from userprofile.models import Profile, Country, Continent, Validation

class ContinentAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'continent')
    list_filter = ('continent', )
    prepopulated_fields = {'slug': ('name', )}

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'firstname', 'surname', 'date')
    search_fields = ('name',)

class ValidationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    search_fields = ('user__username', 'user__first_name')

admin.site.register(Continent, ContinentAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Validation, ValidationAdmin)
