from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Category, Event, EventRegistration, ServiceRequest, User


def home(request):
    return render(request, 'home.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role', 'citizen')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password, role=role)
        user.save()
        messages.success(request, 'Account created! Please log in.')
        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    my_requests = ServiceRequest.objects.filter(submitted_by=user).order_by('-created_at')
    events = Event.objects.filter(date__gte=timezone.localdate()).order_by('date')
    request_count = my_requests.count()

    return render(request, 'dashboard.html', {
        'my_requests': my_requests,
        'events': events,
        'event_count': events.count(),
        'request_count': request_count,
        'open_count': my_requests.filter(status='open').count(),
        'resolved_count': my_requests.filter(status__in=['resolved', 'closed']).count(),
    })


@login_required
def event_list(request):
    events = Event.objects.filter(date__gte=timezone.localdate()).select_related('category').order_by('date')
    category_filter = request.GET.get('category', '').strip()
    if category_filter:
        events = events.filter(category__name=category_filter)

    return render(request, 'events.html', {
        'events': events,
        'categories': Category.objects.order_by('name'),
        'selected_category': category_filter,
    })


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event.objects.select_related('category'), id=event_id)
    is_registered = EventRegistration.objects.filter(event=event, citizen=request.user).exists()
    registrations_count = event.registrations.count()

    return render(request, 'event_detail.html', {
        'event': event,
        'is_registered': is_registered,
        'registrations_count': registrations_count,
    })


@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if event.registrations.count() >= event.capacity:
        messages.error(request, 'This event has reached full capacity.')
        return redirect('event_detail', event_id=event.id)

    registration, created = EventRegistration.objects.get_or_create(
        event=event,
        citizen=request.user,
    )
    if created:
        messages.success(request, f'You are registered for {event.title}!')
    else:
        messages.warning(request, 'You are already registered for this event.')

    return redirect('event_detail', event_id=event.id)


@login_required
def submit_request(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        location = request.POST.get('location')

        ServiceRequest.objects.create(
            title=title,
            description=description,
            category=category,
            location=location,
            submitted_by=request.user,
        )
        messages.success(request, 'Service request submitted!')
        return redirect('my_requests')

    return render(request, 'submit_request.html')


@login_required
def my_requests(request):
    requests = ServiceRequest.objects.filter(submitted_by=request.user).order_by('-created_at')
    return render(request, 'my_requests.html', {'requests': requests})


@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    events = Event.objects.none()
    service_requests = ServiceRequest.objects.none()

    if query:
        events = Event.objects.select_related('category').filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(location__icontains=query)
            | Q(category__name__icontains=query)
        ).order_by('date')

        request_queryset = (
            ServiceRequest.objects.all()
            if request.user.is_staff
            else ServiceRequest.objects.filter(submitted_by=request.user)
        )
        normalized_query = query.replace(' ', '_')
        service_requests = request_queryset.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(location__icontains=query)
            | Q(category__icontains=normalized_query)
            | Q(status__icontains=normalized_query)
        ).order_by('-created_at')

    return render(request, 'search_results.html', {
        'query': query,
        'events': events,
        'service_requests': service_requests,
    })
