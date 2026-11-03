# SmartCity Hub

Community Services & Urban Engagement Platform built with Django.

**Course:** CSE 460 – Software Engineering, Fall 2026  
**Phase:** III, Part I (approximately 20% of the complete project)  
**Author:** Lana Ghanim

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Routes](#routes)
- [Usage](#usage)
- [Data Model](#data-model)
- [Configuration Notes](#configuration-notes)
- [Roadmap](#roadmap)
- [Author](#author)
- [License](#license)

---

## Overview

SmartCity Hub is a web platform that connects citizens with city services, community
events, and local government initiatives. Citizens can browse upcoming events, submit
service requests for city issues, and track each request from submission to resolution.

This repository contains the **Phase III, Part I** implementation.

---

## Features

### Authentication and Accounts

- User registration as a **Citizen** or **Event Organizer**
- Secure login and logout
- Custom user model with role and phone number fields
- Login-protected dashboard, event, and service-request pages

### Community Events

- Browse upcoming community events
- Event cards display title, date, time, location, category, capacity, and price
- Admin management of events through the Django admin site

### Service Requests

- Submit service requests for city issues
- Supported categories:
  - Roads
  - Lighting
  - Sanitation
  - Public Safety
  - Water
  - Noise
- Track request status through five stages: Open, Assigned, In Progress, Resolved, Closed
- Dedicated **My Requests** page for each citizen

### Administrative Panel

Django admin is configured for managing:

- Users
- Categories
- Events
- Service Requests
- Notifications

### User Interface

- Responsive layout built on Bootstrap 5.3
- Custom visual theme and reusable event/request cards
- Status badges, statistics, empty states, and form validation

---

## Technology Stack

| Layer | Technology |
| --- | --- |
| **Backend** | Python 3.14, Django 6.1.2 |
| **Database** | SQLite (development) |
| **Frontend** | HTML5, Bootstrap 5.3, Bootstrap Icons |
| **Styling** | Custom CSS (`static/css/style.css`) |
| **Version Control** | Git, GitHub |

Dependencies are pinned in [`requirements.txt`](requirements.txt).

---

## Project Structure

```text
smartcityhub/
├── core/                     # Main application
│   ├── migrations/           # Database migrations
│   ├── admin.py              # Admin panel configuration
│   ├── models.py             # Database models
│   ├── tests.py              # Test suite (placeholder)
│   ├── urls.py               # Application URL routes
│   └── views.py              # View logic
├── smartcityhub/             # Project configuration
│   ├── settings.py           # Django settings
│   ├── urls.py               # Root URL configuration
│   ├── asgi.py
│   └── wsgi.py
├── static/
│   └── css/
│       └── style.css         # Global theme and components
├── templates/
│   ├── partials/
│   │   ├── _event_card.html  # Reusable event card
│   │   └── _request_card.html  # Reusable request card
│   ├── base.html             # Shared layout, navbar, footer
│   ├── home.html             # Landing page
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── events.html
│   ├── submit_request.html
│   └── my_requests.html
├── db.sqlite3                # Development database
├── manage.py
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- **Python 3.12 or newer** (Django 6.1 requires Python 3.12+)
- `pip`
- Git (optional, for cloning)

### 1. Clone the repository

```bash
git clone https://github.com/lanaghanim/SmartCityHub.git
cd SmartCityHub
```

### 2. Create and activate a virtual environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

> Run `python manage.py makemigrations` only after changing models.

### 5. Create an administrator account

```bash
python manage.py createsuperuser
```

Follow the prompts for username, email, and password.

### 6. Start the development server

```bash
python manage.py runserver
```

### 7. Open the application

Visit: <http://127.0.0.1:8000/>

---

## Routes

| URL | Page | Access |
| --- | --- | --- |
| `/` | Homepage | Public |
| `/register/` | Registration | Public |
| `/login/` | Login | Public |
| `/logout/` | Logout | Authenticated |
| `/dashboard/` | User dashboard | Login required |
| `/events/` | Browse community events | Login required |
| `/submit-request/` | Submit a service request | Login required |
| `/my-requests/` | View submitted requests | Login required |
| `/admin/` | Django admin panel | Staff / superuser |

---

## Usage

### As a Citizen

1. Register an account and sign in.
2. Browse community events on the **Events** page.
3. Submit service requests for city issues from **Report Issue**.
4. Follow each request's status on **My Requests** and the **Dashboard**.

### As an Administrator

1. Sign in to `/admin/` with a superuser account.
2. Create event categories and community events.
3. Review, assign, and update service requests.
4. Manage users and notifications.

---

## Data Model

| Model | Purpose |
| --- | --- |
| `User` | Custom authentication user with `role` and `phone_number` fields |
| `Category` | Event category (name and description) |
| `Event` | Community event details, organizer, capacity, and price |
| `ServiceRequest` | Citizen issue report with category, location, status, and assignee |
| `Notification` | Notification record for a recipient (admin-managed in this phase) |

The custom user model supports five roles: Citizen, City Administrator, Department
Manager, City Worker, and Event Organizer.

---

## Configuration Notes

- The project uses **SQLite** for development. The database is created automatically
  after running migrations.
- `DEBUG = True` and the development `SECRET_KEY` are intended for local development
  only and must not be used in production.
- Static assets are served by Django's development server from `static/`.
  No `collectstatic` step is required for local development.
- Email uses Django's console backend for development.
- `Notification` and event-registration workflows are scheduled for later phases.

---

## Roadmap

### Phase III, Part II (due November 14)

- Full event registration system
- Observer pattern for notifications
- Factory pattern for service request types
- Admin dashboard with assignment features

### Phase III, Part III (due November 21)

- Complete project with all features
- Analytics and reporting
- Content moderation
- UI/UX polish
- Comprehensive testing

### Phase IV (due November 30)

- Technical presentation
- Non-technical marketing presentation

---

## Author

**Lana Ghanim**  
CSE 460 – Software Engineering  
Fall 2026

---

## License

This project is developed for educational purposes as part of CSE 460 at Arizona State
University.
