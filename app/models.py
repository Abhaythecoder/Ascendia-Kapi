# --- file: payapp/app/models.py ---
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class CreatorProfile(models.Model):
    """
    A profile for creators to store their public information.
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

class DonationAttempt(models.Model):
    """
    Tracks each time a QR code is generated for a payment.
    """
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donation_attempts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.creator.username} - ₹{self.amount} ({self.timestamp.date()})'

class Analytics(models.Model):
    """
    Stores analytics data for each creator.
    """
    creator = models.OneToOneField(User, on_delete=models.CASCADE)
    page_views = models.PositiveIntegerField(default=0)
    qr_generations = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.creator.username} Analytics'

@receiver(post_save, sender=User)
def create_analytics(sender, instance, created, **kwargs):
    """
    Automatically creates an Analytics object for a new user.
    """
    if created:
        Analytics.objects.create(creator=instance)