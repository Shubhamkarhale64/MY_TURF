from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from turfapp.models import Turf,Slot,Booking
from sportsapp.models import Sport
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import IntegrityError
from turfapp.models import TurfOwner
from django.contrib.auth.decorators import login_required

def owner_register(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        business_name = request.POST.get("business_name", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not all([name, email, business_name, password, confirm_password]):
            messages.error(request, "Please fill in all fields.")
            return render(request, "owner_register.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "owner_register.html")

        if User.objects.filter(username=email).exists():
            messages.error(request, "This email is already registered.")
            return render(request, "owner_register.html")

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
            )

            TurfOwner.objects.create(
                user=user,
                business_name=business_name,
                verification_status="PENDING",
            )

        except IntegrityError:
            messages.error(request, "Registration failed. Please try again.")
            return render(request, "owner_register.html")

        messages.success(
            request,
            "Registration submitted! Please wait for admin approval.",
        )
        return redirect("owner_login")

    return render(request, "owner_register.html")


def owner_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if hasattr(user, "turf_owner"):

                owner = user.turf_owner

                if owner.verification_status == "VERIFIED":

                    login(request, user)

                    return redirect("owner_dashboard")

                elif owner.verification_status == "PENDING":

                    messages.error(
                        request,
                        "Your account is pending admin approval."
                    )

                else:

                    messages.error(
                        request,
                        "Your owner account has not been approved. Please contact admin."
                    )

            else:

                messages.error(
                    request,
                    "This account is not registered as a Turf Owner."
                )

        else:

            messages.error(
                request,
                "Invalid username or password."
            )

    return render(request, "owner_login.html")

def owner_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("owner_login")

    if not hasattr(request.user, "turf_owner"):
        messages.error(request, "Please login as a turf owner.")
        return redirect("owner_login")

    return render(request, "owner_dashboard.html")

# ADD THIS BELOW owner_login()


def my_turfs(request):
    if not request.user.is_authenticated:
        return redirect("owner_login")

    if not hasattr(request.user, "turf_owner"):
        messages.error(request, "Please login as a turf owner.")
        return redirect("owner_login")

    owner = request.user.turf_owner

    turfs = Turf.objects.filter(
        owner=owner
    ).order_by("-id")

    return render(
        request,
        "my_turfs.html",
        {"turfs": turfs}
    )


def add_turf(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please login as a turf owner first.")
        return redirect("owner_login")

    if not hasattr(request.user, "turf_owner"):
        messages.error(request, "This account is not registered as a turf owner.")
        return redirect("owner_login")

    owner = request.user.turf_owner

    # Keep the rest of your existing add_turf code below this line

    owner = request.user.turf_owner

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

        return redirect("home")

    return render(
        request,
        "add_turf.html",
        {"sports": sports}
    )


@login_required
def edit_turf(request, turf_id):
    owner = getattr(request.user, "turf_owner", None)

    if owner is None:
        messages.error(request, "Please login as a Turf Owner.")
        return redirect("owner_login")

    turf = get_object_or_404(
        Turf,
        id=turf_id,
        owner=owner
    )

    sports = Sport.objects.filter(status=True)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        price = request.POST.get("price_per_hour", "").strip()

        if not name or not price:
            messages.error(request, "Turf name and price are required.")
            return render(request, "edit_turf.html", {
                "turf": turf,
                "sports": sports,
                "selected_sports": turf.turf_sports.values_list(
                    "sport_id", flat=True
                ),
            })

        turf.name = name
        turf.description = request.POST.get("description", "").strip()
        turf.address = request.POST.get("address", "").strip()
        turf.city = request.POST.get("city", "").strip()
        turf.area = request.POST.get("area", "").strip()
        turf.ground_type = request.POST.get("ground_type", "").strip()
        turf.price_per_hour = price

        if request.FILES.get("image"):
            turf.image = request.FILES["image"]

        turf.save()

        turf.turf_sports.all().delete()

        for sport_id in request.POST.getlist("sports"):
            sport = Sport.objects.filter(
                id=sport_id,
                status=True
            ).first()

            if sport:
                turf.turf_sports.create(sport=sport)

        messages.success(request, "Turf updated successfully.")
        return redirect("my_turfs")

    selected_sports = turf.turf_sports.values_list(
        "sport_id", flat=True
    )

    return render(request, "edit_turf.html", {
        "turf": turf,
        "sports": sports,
        "selected_sports": selected_sports,
    })


@login_required
def manage_slots(request):
    # Check whether the logged-in user is a Turf Owner
    owner = getattr(request.user, "turf_owner", None)

    if owner is None:
        messages.error(
            request,
            "Please login using your Turf Owner account."
        )
        return redirect("owner_login")

    # Only show this owner's turfs and slots
    turfs = Turf.objects.filter(owner=owner)
    slots = Slot.objects.filter(
        turf__owner=owner
    ).order_by("date", "start_time")

    if request.method == "POST":
        turf_id = request.POST.get("turf")
        date = request.POST.get("date", "")
        start_time = request.POST.get("start_time", "")
        end_time = request.POST.get("end_time", "")
        price = request.POST.get("price", "")

        # Check required fields
        if not all([turf_id, date, start_time, end_time, price]):
            messages.error(request, "Please fill in all fields.")
            return render(
                request,
                "manage_slots.html",
                {"turfs": turfs, "slots": slots}
            )

        # Check past date
        today = timezone.localdate()

        if date < str(today):
            messages.error(
                request,
                "You cannot create a slot for a past date."
            )
            return render(
                request,
                "manage_slots.html",
                {"turfs": turfs, "slots": slots}
            )

        # Check time range
        if start_time >= end_time:
            messages.error(
                request,
                "End Time must be after Start Time."
            )
            return render(
                request,
                "manage_slots.html",
                {"turfs": turfs, "slots": slots}
            )

        # Verify that this turf belongs to the logged-in owner
        turf = get_object_or_404(
            Turf,
            id=turf_id,
            owner=owner
        )

        # Prevent overlapping slots for the same turf and date
        overlapping_slot = Slot.objects.filter(
            turf=turf,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if overlapping_slot:
            messages.error(
                request,
                "This time slot overlaps with an existing slot."
            )
            return render(
                request,
                "manage_slots.html",
                {"turfs": turfs, "slots": slots}
            )

        # Create slot
        Slot.objects.create(
            turf=turf,
            date=date,
            start_time=start_time,
            end_time=end_time,
            price=price
        )

        messages.success(request, "Slot added successfully.")
        return redirect("manage_slots")

    return render(
        request,
        "manage_slots.html",
        {"turfs": turfs, "slots": slots}
    )

@login_required
def edit_slot(request, slot_id):
    owner = getattr(request.user, "turf_owner", None)

    if owner is None:
        messages.error(request, "Please login as a Turf Owner.")
        return redirect("owner_login")

    slot = get_object_or_404(
        Slot,
        id=slot_id,
        turf__owner=owner
    )

    if slot.status != "AVAILABLE":
        messages.error(request, "Only available slots can be edited.")
        return redirect("manage_slots")

    turfs = Turf.objects.filter(owner=owner)

    slot = get_object_or_404(
        Slot,
        id=slot_id,
        turf__owner=owner
    )

    turfs = Turf.objects.filter(owner=owner)

    if request.method == "POST":

        date = request.POST.get("date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        price = request.POST.get("price")

        # --------------------------------
        # 1. Check past date
        # --------------------------------

        today = timezone.localdate()

        if date < str(today):
            messages.error(
                request,
                "You cannot set a slot to a past date."
            )

            return render(
                request,
                "edit_slot.html",
                {
                    "slot": slot,
                    "turfs": turfs
                }
            )

        # --------------------------------
        # 2. Check Start Time and End Time
        # --------------------------------

        if start_time >= end_time:
            messages.error(
                request,
                "End Time must be after Start Time."
            )

            return render(
                request,
                "edit_slot.html",
                {
                    "slot": slot,
                    "turfs": turfs
                }
            )

        # --------------------------------
        # 3. Check overlapping slots
        # --------------------------------

        overlapping_slot = Slot.objects.filter(
            turf=slot.turf,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(
            id=slot.id
        ).exists()

        if overlapping_slot:
            messages.error(
                request,
                "This time slot overlaps with an existing slot."
            )

            return render(
                request,
                "edit_slot.html",
                {
                    "slot": slot,
                    "turfs": turfs
                }
            )

        # --------------------------------
        # 4. Update slot
        # --------------------------------

        slot.date = date
        slot.start_time = start_time
        slot.end_time = end_time
        slot.price = price

        slot.save()

        messages.success(
            request,
            "Slot updated successfully."
        )

        return redirect("manage_slots")

    return render(
        request,
        "edit_slot.html",
        {
            "slot": slot,
            "turfs": turfs
        }
    )

@login_required
def delete_slot(request, slot_id):
    owner = getattr(request.user, "turf_owner", None)

    if owner is None:
        messages.error(request, "Please login as a Turf Owner.")
        return redirect("owner_login")

    if request.method != "POST":
        return redirect("manage_slots")

    slot = get_object_or_404(
        Slot,
        id=slot_id,
        turf__owner=owner
    )

    if slot.status != "AVAILABLE":
        messages.error(
            request,
            "Only available slots can be deleted."
        )
        return redirect("manage_slots")

    slot.delete()
    messages.success(request, "Slot deleted successfully.")
    return redirect("manage_slots")

def turf_search(request):
    turfs = Turf.objects.filter(status="APPROVED").order_by("rating","name")

    search = request.GET.get("search", "").strip()
    city = request.GET.get("city", "").strip()
    sport_id = request.GET.get("sport", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    if search:
        turfs = turfs.filter(
            name__icontains=search
        )

    if city:
        turfs = turfs.filter(
            city__icontains=city
        )

    if sport_id:
        turfs = turfs.filter(
            turf_sports__sport_id=sport_id
        )

    if max_price:
        turfs = turfs.filter(
            price_per_hour__lte=max_price
        )

    sports = Sport.objects.filter(
        status=True
    ).order_by("name")

    return render(
        request,
        "turf_search.html",
        {
            "turfs": turfs,
            "sports": sports,
            "search": search,
            "city": city,
            "sport_id": sport_id,
            "max_price": max_price,
        }
    )
def turf_detail(request, turf_id):
    turf = get_object_or_404(
        Turf,
        id=turf_id,
        status="APPROVED"
    )

    return render(
        request,
        "turf_detail.html",
        {
            "turf": turf
        }
    )
def turf_slots(request, turf_id):
    turf = get_object_or_404(
        Turf,
        id=turf_id,
        status="APPROVED"
    )

    selected_date = request.GET.get("date")

    slots = Slot.objects.filter(
        turf=turf,
        status="AVAILABLE"
    ).order_by("date", "start_time")

    if selected_date:
        slots = slots.filter(date=selected_date)

    return render(
        request,
        "turf_slots.html",
        {
            "turf": turf,
            "slots": slots,
            "selected_date": selected_date,
        }
    )

def book_slot(request, slot_id):

    # Check customer login
    if not request.user.is_authenticated:
        messages.error(request, "Please login before booking.")
        return redirect("customer_login")

    # Only allow POST requests
    if request.method != "POST":
        return redirect("turf_search")

    # Find an available slot in an approved turf
    slot = get_object_or_404(
        Slot,
        id=slot_id,
        status="AVAILABLE",
        turf__status="APPROVED"
    )

    # Prevent booking past dates
    today = timezone.localdate()

    if slot.date < today:
        messages.error(request, "You cannot book a past slot.")
        return redirect("turf_slots", turf_id=slot.turf.id)

    # Prevent duplicate pending or confirmed bookings
    existing_booking = Booking.objects.filter(
        slot=slot,
        booking_status__in=["PENDING", "CONFIRMED"]
    ).exists()

    if existing_booking:
        messages.error(request, "This slot has already been booked.")
        return redirect("turf_slots", turf_id=slot.turf.id)

    # Create booking
    booking_code = ( f"MT{timezone.now().strftime('%Y%m%d%H%M%S')}{slot.id}")

    booking = Booking.objects.create(
        booking_code=booking_code,
        user=request.user,
        turf=slot.turf,
        slot=slot,
        booking_date=slot.date,
        amount=slot.price,
        booking_status="PENDING",
        payment_status="PENDING"
    )

    messages.success(request, "Booking created successfully.")

    # Redirect to booking summary
    return redirect(
        "booking_summary",
        booking_id=booking.id
    )
def customer_register(request):

    if request.user.is_authenticated:
        return redirect("turf_search")

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not name or not email or not mobile or not password:
            messages.error(
                request,
                "All fields are required."
            )
            return render(request, "customer_register.html")

        if password != confirm_password:
            messages.error(
                request,
                "Passwords do not match."
            )
            return render(request, "customer_register.html")

        if User.objects.filter(username=email).exists():
            messages.error(
                request,
                "An account with this email already exists."
            )
            return render(request, "customer_register.html")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        login(request, user)

        messages.success(
            request,
            "Registration successful."
        )

        return redirect("turf_search")

    return render(
        request,
        "customer_register.html"
    )
def customer_login(request):

    if request.user.is_authenticated:
        return redirect("turf_search")

    if request.method == "POST":

        email = request.POST.get("email", "").strip()
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:

            login(request, user)

            messages.success(
                request,
                "Login successful."
            )

            return redirect("turf_search")

        messages.error(
            request,
            "Invalid email or password."
        )

    return render(
        request,
        "customer_login.html"
    )
@login_required
def booking_summary(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    return render(
        request,
        "booking_summary.html",
        {
            "booking": booking
        }
    )
def my_bookings(request):

    if not request.user.is_authenticated:
        return redirect("customer_login")

    bookings = Booking.objects.filter(
        user=request.user
    ).select_related(
        "turf",
        "slot"
    ).order_by("-created_at")

    return render(
        request,
        "my_bookings.html",
        {
            "bookings": bookings
        }
    )
@login_required
def payment(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    if booking.booking_status != "PENDING":
        messages.error(
            request,
            "This booking cannot be paid."
        )
        return redirect(
            "booking_summary",
            booking_id=booking.id
        )

    if request.method == "POST":

        payment_status = request.POST.get("payment_status")

        if payment_status == "SUCCESS":

            booking.payment_status = "SUCCESS"
            booking.booking_status = "CONFIRMED"
            booking.save()

            booking.slot.status = "BOOKED"
            booking.slot.save()

            messages.success(
                request,
                "Payment successful. Booking confirmed."
            )

            return redirect(
                "booking_summary",
                booking_id=booking.id
            )

        else:

            booking.payment_status = "FAILED"
            booking.save()

            messages.error(
                request,
                "Payment failed."
            )

            return redirect(
                "booking_summary",
                booking_id=booking.id
            )

    return render(
        request,
        "payment.html",
        {
            "booking": booking
        }
    )
def customer_logout(request):
    logout(request)
    return redirect("customer_login")

def customer_profile(request):
    if not request.user.is_authenticated:
        return redirect("customer_login")

    return render(
        request,
        "customer_profile.html",
        {"user": request.user}
    )
def cancel_booking(request, booking_id):
    if not request.user.is_authenticated:
        return redirect("customer_login")

    if request.method != "POST":
        return redirect("my_bookings")

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    if booking.booking_status != "CONFIRMED":
        messages.error(
            request,
            "Only confirmed bookings can be cancelled."
        )
        return redirect("my_bookings")

    booking.booking_status = "CANCELLED"
    booking.save()

    booking.slot.status = "AVAILABLE"
    booking.slot.save()

    messages.success(
        request,
        "Booking cancelled successfully."
    )

    return redirect("my_bookings")

@login_required
def owner_bookings(request):
    owner = getattr(request.user, "turf_owner", None)

    if owner is None:
        messages.error(request, "Please login as a Turf Owner.")
        return redirect("owner_login")

    bookings = Booking.objects.filter(
        turf__owner=owner
    ).select_related(
        "user", "turf", "slot"
    ).order_by("-created_at")

    return render(
        request,
        "owner_bookings.html",
        {"bookings": bookings}
    )

from django.views.decorators.http import require_POST
from django.db import transaction


@login_required
@require_POST
def owner_cancel_booking(request, booking_id):
    owner = getattr(request.user, "turf_owner", None)

    if owner is None:
        messages.error(request, "Please login as a Turf Owner.")
        return redirect("owner_login")

    with transaction.atomic():
        booking = get_object_or_404(
            Booking.objects.select_for_update(),
            id=booking_id,
            turf__owner=owner,
        )

        if booking.booking_status != "CONFIRMED":
            messages.error(
                request,
                "Only confirmed bookings can be cancelled."
            )
            return redirect("owner_bookings")

        slot = Slot.objects.select_for_update().get(
            id=booking.slot_id
        )

        booking.booking_status = "CANCELLED"
        booking.save(update_fields=["booking_status"])

        # Release the slot only if no other active booking uses it.
        other_active_booking = Booking.objects.filter(
            slot=slot,
            booking_status__in=["PENDING", "CONFIRMED"],
        ).exclude(id=booking.id).exists()

        if not other_active_booking:
            slot.status = "AVAILABLE"
            slot.save(update_fields=["status"])

    messages.success(request, "Booking cancelled successfully.")
    return redirect("owner_bookings")