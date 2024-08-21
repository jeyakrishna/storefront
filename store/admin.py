from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.db.models import Count
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html, urlencode
from . import models


# Register your models here.

class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [
            ('<10', 'Low')
        ]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == '<10':
            return queryset.filter(inventory__lt = 10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    # to show only some fields
    # fields = ['title', 'slug']

    # to exclude any fields
    # exclude = ['promotions']

    # read only is used just for show casing purpose and won't be able to make any changes to it

    
    # autocomplete
    autocomplete_fields = ['collection']

    actions = ['clear_inventory']
    # inlines = [TagInline]
    list_display = ['title', 'unit_price', 'inventory_status', 'collection', 'collection_title']
    list_editable = ['unit_price'] # to edit multiple values on one go
    list_per_page = 10
    list_select_related = ['collection']
    list_filter = ['collection', 'last_update', InventoryFilter]
    # prepopulate
    prepopulated_fields = {
        'slug' : ['title']
    }

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'
    
    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory = 0)
        self.message_user(
            request,
            f'{updated_count} products were successfully updated.'
        )


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', 'customer']
    list_per_page = 25
    list_select_related = ['customer']
    autocomplete_fields = ['customer']
    # ordering = ['placed_at', 'id']


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership']
    list_editable = ['membership']
    list_per_page = 20
    ordering = ['first_name', 'last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']
    


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        # input to reverse -> admin:app_model_page
        url = (reverse('admin:store_product_changelist')
               + '?'
               + urlencode({
                   'collection__id' : str(collection.id)
               })
               )
        return format_html('<a href="{}">{}</a>', url, collection.products_count)
        # return collection.products_count
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request) \
                        .annotate(
                            products_count = Count('product')
                        )


# One way to customize the list page, is to add it after models.Product in the below line
# admin.site.register(models.Product, ProductAdmin)
# or can be called using @____(register decorator) above the ProductAdmin class. 
