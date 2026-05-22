from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_user', 'business_user', 'offer_type', 'status', 'price', 'created_at']
    list_filter = ['status', 'offer_type', 'created_at', 'updated_at']
    search_fields = ['customer_user__username', 'business_user__username', 'title']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Users', {
            'fields': ('customer_user', 'business_user')
        }),
        ('Order Details', {
            'fields': ('offer_detail', 'title', 'offer_type', 'price', 'delivery_time_in_days', 'revisions', 'features', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['customer_user', 'business_user', 'offer_detail', 'title', 'offer_type', 'price', 'delivery_time_in_days', 'revisions', 'features']
        return self.readonly_fields
