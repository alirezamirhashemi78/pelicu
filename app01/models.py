from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.utils import timezone
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Person(models.Model):
    name = models.CharField(max_length=100)
    

    class Meta:
        db_table = "persons"


class Movie(models.Model):
    title = models.CharField(max_length=200)
    genres = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    image_path = models.ImageField(upload_to="media/images/", blank=True, null=True, help_text="Main promotional poster")    
    duration_minutes = models.PositiveIntegerField(verbose_name="Duration (minutes)")
    director = models.ManyToManyField(Person, related_name='directed_movies', blank=True)
    actors = models.ManyToManyField(Person, related_name='acted_movies', blank=True)
    imdb_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        default=0.0
    )
    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1888),  # First movie ever made
            MaxValueValidator(timezone.now().year)
        ]
    )    

    class Meta:
        db_table = "movies"



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    signup_date = models.DateField(null=True, blank=True)
    email = models.BooleanField(default=False)
    profile_photo_path = models.ImageField(upload_to="media/images/users/", blank=True, null=True,)    
    interested_movies = models.ManyToManyField(Movie, blank=True,)
    class Meta:
        db_table = 'profiles'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)