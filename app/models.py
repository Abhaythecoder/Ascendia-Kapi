# --- file: payapp/app/models.py ---
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class CreatorProfile(models.Model):
    """
    A profile for creators to store their public information.
    
    Each user will have a CreatorProfile automatically created.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    upi_id = models.CharField(max_length=255, blank=True, null=True, unique=True,
                              help_text="This is where your UPI ID goes")
    bio = models.TextField(blank=True, default="Hi there! I'm a creator. Your support helps me do what I love!",
                              help_text="Your Bio help your followers know more about you")
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a CreatorProfile when a new User is created.
    """
    CreatorProfile.objects.get_or_create(user=instance)
