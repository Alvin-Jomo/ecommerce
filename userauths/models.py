from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    bio = models.CharField(max_length=100, null=True, blank=True)
    is_approved = models.BooleanField(default=False)  # Field to check if user is approved

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

class Profile(models.Model):
    # Define location choices
    LOCATION_CHOICES = [
        ('none', 'none'),
        ('Parklands', 'Parklands'),
        ('Upperhill', 'Upperhill'),
        ('South B/South C', 'South B/South C'),
        ('Buruburu/Donholm', 'Buruburu/Donholm'),
        ('long-distance', 'long-distance')
    ]

    # Define manager choices
    MANAGER_CHOICES = [
        ('none', 'none'),
        ('Regina Auma', 'Regina Auma'),
        ('Elizabeth Okoth', 'Elizabeth Okoth'),
        ('Annette Kitagwa', 'Annette Kitagwa'),
        ('long-distance', 'long-distance')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="image", null=True, blank=True)
    full_name = models.CharField(max_length=200, null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    verified = models.BooleanField(default=False, null=True, blank=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    allocated_funds = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES, default='none')
    manager = models.CharField(max_length=50, choices=MANAGER_CHOICES, null=False, blank=False, default="antony")

    def __str__(self):
        return f"{self.user.username} - {self.full_name} - {self.bio}"

class ContactUs(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    message = models.TextField()

    class Meta:
        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us"

    def __str__(self):
        return self.full_name

# Signals to handle Profile creation
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Profile when a new User is created.
    """
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the Profile whenever the User is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
