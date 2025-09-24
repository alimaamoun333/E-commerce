from rest_framework import serializers
from django.utils.text import slugify
from products.models import Category, Product

class ProductBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'price')  # keep brief; expand as needed

class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    products = serializers.SerializerMethodField()
    slug = serializers.SlugField(required=False)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'products_count', 'products', 'created_at')
        read_only_fields = ('created_at', 'products_count')

    def get_products(self, obj):
        # include nested products only when client asks: ?include_products=true
        request = self.context.get('request', None)
        if request and request.query_params.get('include_products', 'false').lower() in ('1','true','yes'):
            qs = obj.products.all()  # related_name 'products'
            return ProductBriefSerializer(qs, many=True).data
        return []

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Category name must be at least 2 characters.")
        # unique check (case-insensitive)
        qs = Category.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Category with this name already exists.")
        return value

    def validate(self, data):
        # ensure slug exists / unique
        slug = data.get('slug') or (slugify(data.get('name')) if data.get('name') else None)
        if slug:
            qs = Category.objects.filter(slug=slug)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"slug": "This slug is already in use."})
            data['slug'] = slug
        return data
