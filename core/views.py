from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, ServiceRequest, User


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
    events = Event.objects.all().order_by('date')
    return render(request, 'dashboard.html', {
        'my_requests': my_requests,
        'events': events,
        'request_count': my_requests.count(),
        'open_count': my_requests.filter(status='open').count(),
        'resolved_count': my_requests.filter(status__in=['resolved', 'closed']).count(),
    })


@login_required
def event_list(request):
    events = Event.objects.all().order_by('date')
    return render(request, 'events.html', {'events': events})


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