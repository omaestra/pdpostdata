from products.models import Product, ProductImage
from rest_framework import serializers


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = (
            'image', 'active',
        )


class ProductSerializer(serializers.ModelSerializer):

    product_images = ProductImageSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            'title', 'description', 'category', 'price', 'sale_price', 'slug', 'image_total', 'timestamp',
            'updated', 'active', 'product_images',
        )
