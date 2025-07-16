from rest_framework import serializers
from decimal import Decimal
from .models import Product, Collection, Review, Cart, CartItem
from pprint import pprint

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    id = serializers.IntegerField(read_only = True)
    title = serializers.CharField(max_length = 255)
    products_count = serializers.IntegerField(read_only = True)

class ProductSerializer(serializers.ModelSerializer):
    '''
    { "title" : "a", "slug" : "a" , "collection" : 1, "unit_price" : 1, "inventory" : 1 }
    '''
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection']
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')    
    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price'] 

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name='calculate_total_price')

    def calculate_total_price(self, cart_item : CartItem):
        return cart_item.product.unit_price * cart_item.quantity

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']

    id = serializers.UUIDField(read_only = True)
    items = CartItemSerializer(many = True)

    total_price = serializers.SerializerMethodField(method_name='calculate_total_price')

    def calculate_total_price(self, cart : Cart):
        total = 0
        for item in cart.items.all():
            total += item.quantity * item.product.unit_price
        return total



