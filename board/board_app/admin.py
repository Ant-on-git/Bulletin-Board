from django.contrib import admin
from .models import Category, AdCategory, Advertisement, AdFiles, Reply, Profile, OneTimeCode

# Register your models here.


class AdCategoryInline(admin.TabularInline):
    model = AdCategory
    extra = 0


class AdFilesInline(admin.TabularInline):
    model = AdFiles
    extra = 0


class AdvertisementAdmin(admin.ModelAdmin):
    inlines = (AdFilesInline, AdCategoryInline)
    list_display = ('id', 'title', 'user', 'text')


class AdFilesAdmin(admin.ModelAdmin):
    list_display = ('ad', 'file')


admin.site.register(Advertisement, AdvertisementAdmin)
admin.site.register(AdFiles, AdFilesAdmin)
admin.site.register(Reply)
admin.site.register(Category)
admin.site.register(Profile)
admin.site.register(OneTimeCode)