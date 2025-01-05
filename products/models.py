import os
from django.db import models
from django.core.exceptions import ValidationError

def validate_image(file):
    ext = os.path.splitext(file.name)[1].lower()
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if ext not in valid_extensions:
        raise ValidationError(f"Invalid file extension. Allowed extensions are: {', '.join(valid_extensions)}")


def product_image_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f'product_images/{instance.pk}_1{ext}'


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(
        upload_to=product_image_path,
        blank=True,
        null=True,
        validators=[validate_image]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
