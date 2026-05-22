from django.contrib import admin
from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    model = OfferDetail
    extra = 0
    fields = ['offer_type', 'title', 'price', 'delivery_time_in_days', 'revisions']
    readonly_fields = []


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OfferDetailInline]
    fieldsets = (
        ('Offer Information', {
            'fields': ('user', 'title', 'image', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = ['offer', 'offer_type', 'price', 'delivery_time_in_days', 'revisions']
    list_filter = ['offer_type', 'created_at']
    search_fields = ['offer__title', 'title', 'offer__user__username']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Offer Reference', {
            'fields': ('offer',)
        }),
        ('Details', {
            'fields': ('offer_type', 'title', 'price', 'delivery_time_in_days', 'revisions', 'features')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
