from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Listing, Category, Watchlist


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


def listing(request, pk):
    watchlist = Watchlist.objects.get(user=request.user).listings.all()
    listing = Listing.objects.get(id=pk)
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist": watchlist,
    })


def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories,
    })


def watchlist(request):
    try:
        watchlist = Watchlist.objects.get(user=request.user)
        listings = watchlist.listings.all()
        return render(request, "auctions/watchlist.html", {
            "listings": listings,
        })
    except:
        return render(request, "auctions/watchlist.html")


def toggle_watchlist_item(request, id):
    # Get the listing we want to add or remove
    listing = Listing.objects.get(id=id)
    # Try to get watchlist if user has already created one
    try:
        # store all the watch lists
        watchlists = Watchlist.objects.all()
        # get the watch list our user
        user_watchlist = watchlists.get(user=request.user)
        # if listing is in the watchlist remove it
        if listing in user_watchlist.listings.all():
            user_watchlist.listings.remove(listing)
        # else add listing to the watchlist
        else:
            user_watchlist.listings.add(listing)
        # and return to listing page
        return redirect(f"/listing/{id}")

    # Except if user does'nt have any watchlist then create a new one and add listing to it
    except ObjectDoesNotExist:
        # Create new watchlist for the user
        new_watchlist = Watchlist.objects.create(user=request.user)
        # save it
        new_watchlist.save()
        # add listing to it
        new_watchlist.listings.add(listing)
        # return to listing page
        return redirect(f"/listing/{id}")


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


def update(request, pk):
    post = Listing.objects.get(id=pk)
    form = CreateListing(instance=post)
    # if method if post
    if request.method == "POST":
        form = CreateListing(request.POST, request.FILES, instance=post)
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
