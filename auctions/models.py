from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # id, name, email

    def __str__(self):
        return f"{self.username}"


class Category(models.Model):
    # id, category
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.category}"


class Listing(models.Model):
    # id, user_id, category_id, title, details, image_url, bid, comments, timestamp
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, blank=True)
    title = models.CharField(max_length=90)
    details = models.CharField(max_length=1000)
    image_url = models.CharField(max_length=500)
    bid = models.IntegerField(blank=True)
    # comments = models.ManyToManyField(Comment)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} create at {self.timestamp}"


class Comment(models.Model):
    # id, list_id, user_id, comment
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=4000)

    def __str__(self):
        return f"{self.user} - {self.listing}: {self.comment}"


class Watchlist(models.Model):
    # id, user_id, list_id
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField(Listing)

    def __str__(self):
        return f"{self.user}: {self.listings}"
