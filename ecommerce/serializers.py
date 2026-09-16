from rest_framework import serializers
from .models import User, Category, Product, ProductVariant

class UserSerializer(serializers.ModelSerializer):
    order_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'role', 'is_active', 'is_staff', 'created_at', 'updated_at', 'order_count',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'order_count',
        ]

    def get_order_count(self, obj):
        return obj.order.count()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=8)

    class Meta:
        model = User
        fields = [
            'name', 'email', 'password',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = User(
            **validated_data
        )

        user.set_password(password)
        user.save()

        return user


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'products_count']
        read_only_fields = ['id', 'products_count']

    def get_products_count(self, obj):
        return obj.products.count()


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    reviews_count = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'stock', 'images', 'category', 'category_name', 'reviews_count', 'in_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'category_name', 'reviews_count', 'in_stock', 'created_at', 'updated_at']

    def get_reviews_count(self, obj):
        return obj.reviews.count()
    
    def get_in_stock(self, obj):
        return obj.stock > 0


class ProductVariantSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    effective_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant

        fields = [
            'id', 'product', 'product_name', 'size', 'color', 'color_hex', 'stock', 'price', 'effective_price', 'in_stock', 'created_at', 'updated_at',
        ]

        read_only_fields = [
            'id', 'product_name', 'effective_price', 'in_stock', 'created_at', 'updated_at',
        ]

    def get_effective_price(self, obj):
        # Use variant price if available,
        # otherwise use the product's base price
        if obj.price is not None:
            return obj.price

        return obj.product.price

    def get_in_stock(self, obj):
        return obj.stock > 0


