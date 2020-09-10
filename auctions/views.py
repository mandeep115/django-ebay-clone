from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, Category


class CreateListing(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['user', 'title', 'categories', 'details', 'image_url', 'bid']
        widgets = {
            'categories': forms.CheckboxSelectMultiple(),
            'user': forms.HiddenInput(),
        }


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
    })

def listing(request, id):
    listing = Listing.objects.get(id=id)
    return render(request, "auctions/listing.html", {
        "listing": listing,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create(request):

    # Passing initial value of user who is currently logdin
    form = CreateListing(initial={'user': request.user})
    # if method if post
    if request.method == "POST":
        form = CreateListing(request.POST, request.FILES)
        # Cheking if form is valid
        if form.is_valid():
            # saving the form
            form.save()
            # redirecting user to all listings
            return HttpResponseRedirect(reverse("index"))
    # return an empty form with user as initial value
    return render(request, "auctions/create.html", {
        "form": form
    })
