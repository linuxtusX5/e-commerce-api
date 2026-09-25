from rest_framework import serializers
from django.utils import timezone
from .models import User, Category, Product, ProductVariant, Order, OrderItem, WishlistItem, Address, Review, Coupon, CartItem

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


class CouponSerializer(serializers.ModelSerializer):
    is_valid = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'type', 'value', 'min_order', 'max_uses', 'used_count', 'expires_at', 'active', 'is_valid', 'created_at',
        ]

        read_only_fields = [
            'id', 'used_count', 'is_valid', 'created_at',
        ]

    def validate_code(self, value):
        return value.upper().strip()

    def validate(self, attrs):
        coupon_type = attrs.get(
            'type',
            getattr(self.instance, 'type', None)
        )

        value = attrs.get(
            'value',
            getattr(self.instance, 'value', None)
        )

        if coupon_type == 'PERCENTAGE' and value > 100:
            raise serializers.ValidationError({
                'value': 'Percentage discount cannot exceed 100.'
            })

        if value is not None and value < 0:
            raise serializers.ValidationError({
                'value': 'Discount value cannot be negative.'
            })

        return attrs

    def get_is_valid(self, obj):
        if not obj.active:
            return False

        if (
            obj.expires_at is not None
            and obj.expires_at <= timezone.now()
        ):
            return False

        if (
            obj.max_uses is not None
            and obj.used_count >= obj.max_uses
        ):
            return False

        return True


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    product_image = serializers.SerializerMethodField()

    variant_size = serializers.CharField(
        source='variant.size',
        read_only=True
    )

    variant_color = serializers.CharField(
        source='variant.color',
        read_only=True
    )

    variant_price = serializers.DecimalField(
        source='variant.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'user', 'product', 'product_name', 'product_price', 'product_image', 'variant', 'variant_size', 'variant_color', 'variant_price', 'quantity', 'subtotal',
        ]

        read_only_fields = [
            'id', 'user', 'product_name', 'product_price', 'product_image', 'variant_size', 'variant_color', 'variant_price', 'subtotal',
        ]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Quantity must be at least 1.'
            )

        return value

    def validate(self, attrs):
        product = attrs.get('product')
        variant = attrs.get('variant')
        quantity = attrs.get('quantity', 1)

        if variant:
            if variant.product_id != product.id:
                raise serializers.ValidationError({
                    'variant': (
                        'This variant does not belong '
                        'to the selected product.'
                    )
                })

            if quantity > variant.stock:
                raise serializers.ValidationError({
                    'quantity': (
                        f"Only {variant.stock} items are available."
                    )
                })

        else:
            if quantity > product.stock:
                raise serializers.ValidationError({
                    'quantity': (
                        f"Only {product.stock} items are available."
                    )
                })

        return attrs

    def get_product_image(self, obj):
        if obj.product.images:
            return obj.product.images[0]

        return None

    def get_subtotal(self, obj):
        if obj.variant and obj.variant.price is not None:
            price = obj.variant.price
        else:
            price = obj.product.price

        return price * obj.quantity