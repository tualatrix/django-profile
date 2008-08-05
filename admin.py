from django.contrib import admin
from userprofile.models import Profile, Validation

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'firstname', 'surname', 'date')
    search_fields = ('name',)

class ValidationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    search_fields = ('user__username', 'user__first_name')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Validation, ValidationAdmin)
