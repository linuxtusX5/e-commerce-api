from django.test import TestCase
from rest_framework.test import APIRequestFactory

from ecommerce.models import Category, Order, Product, User
from ecommerce.serializers import OrderSerializer


class OrderSerializerTests(TestCase):
    def test_create_order_sets_total_before_saving(self):
        user = User.objects.create_user(
            email="buyer@example.com",
            password="secret123",
            name="Buyer",
        )
        category = Category.objects.create(name="Books", slug="books")
        product = Product.objects.create(
            name="Django Guide",
            slug="django-guide",
            description="A helpful guide",
            price=15.5,
            stock=10,
            category=category,
        )

        request = APIRequestFactory().post("/api/orders/")
        request.user = user

        serializer = OrderSerializer(
            data={
                "user": user.id,
                "status": "PENDING",
                "order_items": [
                    {"product": product.id, "quantity": 2},
                ],
            },
            context={"request": request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()

        self.assertEqual(order.total, 31.0)
        self.assertEqual(order.order_items.count(), 1)
        self.assertEqual(Order.objects.count(), 1)
