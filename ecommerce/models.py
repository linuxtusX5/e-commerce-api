from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager


# =========================================================
# User
# =========================================================

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        if password:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(
            email=email,
            password=password,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        USER = "USER", "User"
        ADMIN = "ADMIN", "Admin"

    name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    email = models.EmailField(
        unique=True
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


# =========================================================
# Password Reset Token
# =========================================================

class PasswordResetToken(models.Model):
    id = models.BigAutoField(primary_key=True)

    email = models.EmailField(
        unique=True,
        db_index=True
    )

    token = models.CharField(
        max_length=255,
        unique=True
    )

    expires = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.email


# =========================================================
# Category
# =========================================================

class Category(models.Model):
    id = models.BigAutoField(primary_key=True)

    name = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        unique=True
    )

    image = models.URLField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


# =========================================================
# Product
# =========================================================

class Product(models.Model):
    id = models.BigAutoField(primary_key=True)

    name = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        unique=True
    )

    description = models.TextField()

    price = models.FloatField()

    stock = models.IntegerField()

    # Prisma String[]
    images = models.JSONField(
        default=list,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


# =========================================================
# Product Variant
# =========================================================

class ProductVariant(models.Model):
    id = models.BigAutoField(primary_key=True)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    size = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    color = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    color_hex = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    stock = models.IntegerField(
        default=0
    )

    # null = use product base price
    price = models.FloatField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "size", "color"],
                name="unique_product_variant"
            )
        ]

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color}"

