from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import User, Category, Product, ProductVariant, Order, WishlistItem, Address, Review, Coupon
from .serializers import UserSerializer, RegisterSerializer, CategorySerializer, ProductSerializer, ProductVariantSerializer, OrderSerializer, WishlistItemSerializer, AddressSerializer, ReviewSerializer, CouponSerializer
from rest_framework.exceptions import PermissionDenied

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        return Response({
            'message': 'User Registerd Successfully',
            'user': RegisterSerializer(user).data
        }, status = status.HTTP_201_CREATED)

    return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ['name', 'created_at']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'slug', 'category__name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductSerializer
        return ProductSerializer


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.select_related('product').all()

    serializer_class = ProductVariantSerializer

    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter,]

    filterset_fields = ['product', 'size', 'color',]

    search_fields = ['size', 'color', 'product__name',]

    ordering_fields = ['price', 'stock', 'created_at',]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('user','coupon').prefetch_related('order_items__product','order_items__variant').all()

    serializer_class = OrderSerializer

    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter,]

    filterset_fields = ['status','user','coupon',]

    search_fields = ['payment_id','user__email','user__name',]

    ordering_fields = ['total','status','created_at','updated_at',]

    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        # Admin/staff can see all orders
        if user.is_staff:
            return self.queryset

        # Normal users can only see their own orders
        return self.queryset.filter(user=user)


class WishlistItemViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]

    queryset = WishlistItem.objects.select_related( 'user', 'product' ).all()

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ['product',]

    search_fields = [ 'product__name', 'product__slug', ]

    ordering_fields = ['created_at',]

    ordering = ['-created_at']

    def get_queryset(self):
        return self.queryset.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    queryset = Address.objects.all()

    filter_backends = [ filters.SearchFilter, filters.OrderingFilter, ]

    filterset_fields = [
        'is_default', 'country', 'state', 'city',
    ]

    search_fields = [
        'label', 'first_name', 'last_name', 'line1', 'city', 'state', 'postal_code', 'phone',
    ]

    ordering_fields = [
        'created_at', 'updated_at', 'is_default', 'city',
    ]

    ordering = ['-is_default', '-created_at']

    def get_queryset(self):
        return Address.objects.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        if serializer.validated_data.get('is_default', False):
            Address.objects.filter(
                user=self.request.user,
                is_default=True
            ).update(
                is_default=False
            )

        serializer.save(
            user=self.request.user
        )

    def perform_update(self, serializer):
        if serializer.validated_data.get('is_default', False):
            Address.objects.filter(
                user=self.request.user,
                is_default=True
            ).exclude(
                id=self.get_object().id
            ).update(
                is_default=False
            )

        serializer.save()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    queryset = Review.objects.select_related('user', 'product').all()

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        'product', 'rating', 'user',
    ]

    search_fields = [
        'title', 'body', 'user__name', 'product__name',
    ]

    ordering_fields = [
        'rating', 'created_at', 'updated_at',
    ]

    ordering = ['-created_at']

    def get_queryset(self):
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        review = self.get_object()
        
        if review.user != self.request.user:
            raise PermissionDenied('You can only update your own reviews.')

        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied('You can only delete your own reviews.')

        instance.delete()


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        'type', 'active',
    ]

    search_fields = [
        'code',
    ]

    ordering_fields = [
        'created_at', 'expires_at', 'value', 'used_count',
    ]

    ordering = ['-created_at']

    def get_queryset(self):
        return self.queryset

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied(
                'Only staff users can create coupons.'
            )

        serializer.save()

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied(
                'Only staff users can update coupons.'
            )

        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied(
                'Only staff users can delete coupons.'
            )

        instance.delete()

