from django.db import models

class Comic(models.Model):
    STATUS_CHOICES = [
        ('reading', 'Читаю'),
        ('completed', 'Прочитано'),
        ('wishlist', 'Хочу прочитать'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    author = models.CharField(max_length=200, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} [{self.status}]"
