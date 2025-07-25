from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.urls import reverse
from django.utils.html import format_html, urlencode

from . import models
# Register your models here.



class InventoryFilter(admin.SimpleListFilter):
    title = "Inventory"
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt = 10)
    
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug' : ['title']
    }
    exclude = ["promotions"]
    actions = ['clear_inventory']
    search_fields = ['title']
    list_display = ["title", "unit_price", "inventory_status", 'collection_title']
    list_editable = ["unit_price"]
    list_per_page = 10
    list_select_related = ['collection']
    list_filter = ['collection', 'last_update', InventoryFilter] 


    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        if product.inventory < 10:
            return "Low"
        return "OK"
    
    @admin.action(description="clear inventory")
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory = 0)
        self.message_user(request, f'{updated_count} products were successfully updated', messages.SUCCESS)



@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership"]
    list_editable = ["membership"]
    search_fields = ['first_name__istartswith', 'last_name__istartswith']
    list_select_related = ['user']
    ordering = ["user__first_name", "user__last_name"]
    list_per_page = 10


class OrderItemInline(admin.StackedInline):
    model = models.OrderItem
    autocomplete_fields = ['product']
    extra = 0
    min_num = 1
    max_num = 10

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ["id", "placed_at", "customer"]

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'product_count']
    search_fields = ['title']
    @admin.display(ordering = "product_count")
    def product_count(self, collection):
        url = reverse("admin:store_product_changelist") + "?" + urlencode({'collection__id' : str(collection.id)})
        return format_html("<a href ='{}'> {} </a>", url, collection.product_count)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count = Count('products')
        )

# admin.site.register(models.Collection)
# admin.site.register(models.Product, ProductAdmin)