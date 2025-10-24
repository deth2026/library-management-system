from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=200, unique=True)
    biography = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Book(models.Model):
    image = models.ImageField(upload_to='imgs/books/', blank=True, null=True)
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    copies = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='imgs/profile_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        profile = instance.userprofile
        profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.get_or_create(user=instance)