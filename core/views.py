from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date

from .models import Category, Department, Event, EventRegistration, ServiceRequest, User


def home(request):
    return render(request, 'home.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role', 'citizen')
        if role not in ('citizen', 'organizer'):
            role = 'citizen'

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
    events = (
        Event.objects.filter(date__gte=timezone.localdate())
        .select_related('category')
        .annotate(registration_count=Count('registrations'))
    )

    keyword = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '').strip()
    date_filter = request.GET.get('date', '').strip()
    location_filter = request.GET.get('location', '').strip()
    price_filter = request.GET.get('price', '').strip()
    sort_filter = request.GET.get('sort', '').strip()

    if keyword:
        events = events.filter(
            Q(title__icontains=keyword)
            | Q(description__icontains=keyword)
            | Q(location__icontains=keyword)
            | Q(category__name__icontains=keyword)
        )
    if category_filter:
        events = events.filter(category__name=category_filter)
    if date_filter:
        parsed_date = parse_date(date_filter)
        if parsed_date:
            events = events.filter(date=parsed_date)
        else:
            messages.warning(request, 'The date filter could not be read. Showing all dates.')
    if location_filter:
        events = events.filter(location__icontains=location_filter)
    if price_filter == 'free':
        events = events.filter(price=0)
    elif price_filter == 'paid':
        events = events.filter(price__gt=0)

    if sort_filter == 'popular':
        events = events.order_by('-registration_count', 'date')
    else:
        events = events.order_by('date')

    has_filters = any([
        keyword,
        category_filter,
        date_filter,
        location_filter,
        price_filter,
        sort_filter,
    ])

    return render(request, 'events.html', {
        'events': events,
        'categories': Category.objects.order_by('name'),
        'selected_category': category_filter,
        'search_query': keyword,
        'selected_date': date_filter,
        'selected_location': location_filter,
        'selected_price': price_filter,
        'selected_sort': sort_filter,
        'has_filters': has_filters,
    })


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event.objects.select_related('category', 'organizer'), id=event_id)
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

    if event.date < timezone.localdate():
        messages.error(request, 'This event has already taken place.')
        return redirect('event_detail', event_id=event.id)

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
    requests = (
        ServiceRequest.objects.filter(submitted_by=request.user)
        .select_related('department', 'assigned_to')
        .order_by('-created_at')
    )
    return render(request, 'my_requests.html', {'requests': requests})


@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    events = Event.objects.none()
    service_requests = ServiceRequest.objects.none()

    if query:
        events = (
            Event.objects.select_related('category')
            .annotate(registration_count=Count('registrations'))
            .filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(location__icontains=query)
                | Q(category__name__icontains=query)
            )
            .order_by('date')
        )

        can_view_all_requests = (
            request.user.is_staff
            or request.user.role in ('admin', 'manager')
            or request.user.is_superuser
        )
        request_queryset = ServiceRequest.objects.select_related(
            'department', 'assigned_to',
        )
        if not can_view_all_requests:
            request_queryset = request_queryset.filter(submitted_by=request.user)
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


@login_required
def admin_dashboard(request):
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Admins only.')
        return redirect('dashboard')

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        new_status = request.POST.get('status')
        valid_statuses = {value for value, _ in ServiceRequest.STATUS_CHOICES}

        if request_id and new_status in valid_statuses:
            service_request = get_object_or_404(ServiceRequest, id=request_id)
            service_request.status = new_status
            service_request.save(update_fields=['status', 'updated_at'])
            messages.success(request, f'Request #{request_id} updated to {service_request.get_status_display()}.')
        else:
            messages.error(request, 'Could not update the service request.')

        return redirect('admin_dashboard')

    all_requests = (
        ServiceRequest.objects.select_related('submitted_by', 'department', 'assigned_to')
        .order_by('-created_at')
    )
    all_events = (
        Event.objects.select_related('category')
        .annotate(registration_count=Count('registrations'))
        .order_by('-date')
    )

    return render(request, 'admin_dashboard.html', {
        'all_requests': all_requests,
        'all_events': all_events,
        'status_choices': ServiceRequest.STATUS_CHOICES,
    })


@login_required
def department_dashboard(request):
    if (
        request.user.role not in ('manager', 'admin')
        and not request.user.is_superuser
    ):
        messages.error(request, 'Access denied. Department managers and admins only.')
        return redirect('dashboard')

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        new_status = request.POST.get('status')
        department_id = request.POST.get('department', '').strip()
        valid_statuses = {value for value, _ in ServiceRequest.STATUS_CHOICES}

        if request_id and new_status in valid_statuses:
            service_request = get_object_or_404(ServiceRequest, id=request_id)
            service_request.status = new_status
            service_request.department = (
                get_object_or_404(Department, id=department_id)
                if department_id
                else None
            )
            service_request.save(update_fields=['status', 'department', 'updated_at'])
            messages.success(
                request,
                f'Request #{request_id} updated to '
                f'{service_request.get_status_display()}.',
            )
        else:
            messages.error(request, 'Could not update the service request.')

        return redirect('department_dashboard')

    all_requests = (
        ServiceRequest.objects.select_related(
            'submitted_by', 'department', 'assigned_to',
        )
        .order_by('-created_at')
    )

    return render(request, 'department_dashboard.html', {
        'all_requests': all_requests,
        'departments': Department.objects.order_by('name'),
        'status_choices': ServiceRequest.STATUS_CHOICES,
    })


@login_required
def request_detail(request, request_id):
    service_request = get_object_or_404(
        ServiceRequest.objects.select_related(
            'submitted_by', 'department', 'assigned_to',
        ),
        id=request_id,
    )

    can_view = (
        request.user == service_request.submitted_by
        or request.user == service_request.assigned_to
        or request.user.role in ('admin', 'manager')
        or request.user.is_staff
        or request.user.is_superuser
    )
    if not can_view:
        messages.error(request, 'You do not have access to that service request.')
        return redirect('my_requests')

    statuses = [value for value, _ in ServiceRequest.STATUS_CHOICES]
    current_index = (
        statuses.index(service_request.status)
        if service_request.status in statuses
        else 0
    )
    status_steps = [
        {
            'value': value,
            'label': label,
            'done': index <= current_index,
            'current': index == current_index,
        }
        for index, (value, label) in enumerate(ServiceRequest.STATUS_CHOICES)
    ]

    return render(request, 'request_detail.html', {
        'service_request': service_request,
        'status_steps': status_steps,
    })
