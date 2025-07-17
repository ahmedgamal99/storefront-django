from rest_framework import serializers
from decimal import Decimal
from .models import Product, Collection, Review, Cart, CartItem, Customer
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
    items = CartItemSerializer(read_only = True, many = True)

    total_price = serializers.SerializerMethodField(method_name='calculate_total_price')

    def calculate_total_price(self, cart : Cart):
        total = 0
        for item in cart.items.all():
            total += item.quantity * item.product.unit_price
        return total

class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No Product with the passed id")
        return value
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            # Update if exists
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id = product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # Create if it doesn't exist
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        
        return self.instance

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only = True)
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']
