
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from turfapp.models import Turf
from sportsapp.models import Sport


@login_required
def add_turf(request):
    # Check whether the logged-in user is a turf owner
    if not hasattr(request.user, "turf_owner"):
        messages.error(request, "Only turf owners can add a turf.")
        return redirect("home")

    owner = request.user.turf_owner

    # Only verified owners can add turfs
    if owner.verification_status != "VERIFIED":
        messages.error(request, "Your owner account is not verified yet.")
        return redirect("home")

    sports = Sport.objects.filter(status=True)

    if request.method == "POST":
        turf = Turf.objects.create(
            owner=owner,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            area=request.POST.get("area"),
            ground_type=request.POST.get("ground_type"),
            price_per_hour=request.POST.get("price_per_hour"),
            image=request.FILES.get("image"),
        )

        selected_sports = request.POST.getlist("sports")

        for sport_id in selected_sports:
            sport = Sport.objects.filter(
                id=sport_id,
                status=True
            ).first()

            if sport:
                turf.turf_sports.create(sport=sport)

        messages.success(
            request,
            "Turf submitted successfully for admin approval."
        )
        return redirect("home")

    return render(request, "add_turf.html", {"sports": sports})