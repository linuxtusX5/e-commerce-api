from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import User, Category, Product, ProductVariant, Order, WishlistItem
from .serializers import UserSerializer, RegisterSerializer, CategorySerializer, ProductSerializer, ProductVariantSerializer, OrderSerializer, WishlistItemSerializer

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