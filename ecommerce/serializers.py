from rest_framework import serializers
from .models import User, Category, Product, ProductVariant, Order, OrderItem, WishlistItem, Address, Review

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


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'variant', 'quantity', 'price',
        ]

        read_only_fields = [
            'id', 'product_name', 'price',
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        source="order_items",
        many=True,
        read_only=True
    )

    user_name = serializers.CharField(
        source="user.name",
        read_only=True
    )

    order_items = OrderItemSerializer(
        many=True,
        write_only=True,
        required=True
    )


    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_name', 'total', 'status', 'coupon', 'discount', 'payment_id', 'items', 'order_items', 'created_at', 'updated_at',
        ]

        read_only_fields = [
            'id', 'user', 'user_name', 'total', 'discount', 'payment_id', 'items', 'created_at', 'updated_at',
        ]


    def create(self, validated_data):
        order_items_data = validated_data.pop("order_items")

        user = self.context["request"].user
        total = 0

        for item_data in order_items_data:
            product = item_data["product"]
            variant = item_data.get("variant")
            quantity = item_data["quantity"]

            # Use variant price if available,
            # otherwise use product price.
            if variant and variant.price is not None:
                price = variant.price
            else:
                price = product.price

            total += price * quantity

        order = Order.objects.create(
            user=user,
            total=total,
            **validated_data
        )

        for item_data in order_items_data:
            product = item_data["product"]
            variant = item_data.get("variant")
            quantity = item_data["quantity"]

            if variant and variant.price is not None:
                price = variant.price
            else:
                price = product.price

            OrderItem.objects.create(
                order=order,
                product=product,
                variant=variant,
                quantity=quantity,
                price=price
            )

        return order


class WishlistItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField( source='product.name', read_only=True )

    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    product_image = serializers.SerializerMethodField()

    class Meta:
        model = WishlistItem
        fields = [
            'id', 'user', 'product', 'product_name', 'product_price', 'product_image', 'created_at',
        ]

        read_only_fields = [
            'id', 'user', 'product_name', 'product_price', 'product_image', 'created_at',
        ]

    def get_product_image(self, obj):
        if obj.product.images:
            return obj.product.images[0]

        return None


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'user', 'label', 'first_name', 'last_name', 'line1', 'line2', 'city', 'state', 'postal_code', 'country', 'phone', 'is_default', 'created_at', 'updated_at',
        ]

        read_only_fields = [
            'id', 'user', 'created_at', 'updated_at',
        ]


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source='user.name',
        read_only=True
    )

    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_name', 'product', 'product_name', 'rating', 'title', 'body', 'created_at', 'updated_at',
        ]

        read_only_fields = [
            'id', 'user', 'user_name', 'product_name', 'created_at', 'updated_at',
        ]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                'Rating must be between 1 and 5.'
            )

        return value


