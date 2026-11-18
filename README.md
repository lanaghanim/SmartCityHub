# SmartCity Hub

> **Phase III, Part 3 submission:** Start here - [PHASE3_PART3.md](PHASE3_PART3.md)
> contains the new features, where to find them, and how to test them.
>
> Looking for Part 2? See [PHASE3_PART2.md](PHASE3_PART2.md).

Community Services & Urban Engagement Platform built with Django.

- **Course:** CSE 460 – Software Engineering, Fall 2026
- **Phase:** III, Part III
- **Author:** Lana Ghanim

---

## Table of Contents

- [Phase III, Part 3 Features](PHASE3_PART3.md)
- [Phase III, Part 2 Features](PHASE3_PART2.md)
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

This repository contains the **Phase III, Part III** implementation.

### What Was Added in Part 3

This part builds on Parts 1 and 2 with event discovery, request tracking, and
department operations:

- **Event discovery** — the Events page now supports keyword search plus category,
  exact-date, location, free/paid, and popularity filters. Filters can be combined
  and are preserved in the URL so results can be shared.
- **Service request progress tracking** — citizens can open any request from
  **My Requests** or the dashboard and see a status timeline, progress bar,
  assigned department, assignee, and last update time. Access is limited to the
  request owner, assigned worker, department managers, and administrators.
- **Department operations** — a new `Department` model and `ServiceRequest.department`
  field let department managers route requests to a department and update the
  request status from a dedicated dashboard.
- **Admin tooling** — the Django admin user form now exposes the custom `role` and
  `phone_number` fields, so an administrator can promote a user to Department
  Manager. Departments are registered in the Django admin site.
- **Regression tests** — `core/tests.py` now contains 13 tests covering the new
  event filters, request progress access rules, and department dashboard updates.

The sections below explain how to run the project, use the new features, and
understand the updated data model.

For the grader-friendly walkthrough, open **[PHASE3_PART3.md](PHASE3_PART3.md)**.

---

## Features

### Authentication and Accounts

- User registration as a **Citizen** or **Event Organizer**
- Secure login and logout
- Custom user model with role and phone number fields
- Login-protected dashboard, event, and service-request pages

### Community Events

- Browse upcoming community events
- Search events by keyword and filter by category, date, location, and free/paid
  price, then sort by date or popularity
- Open an event detail page with the full description, date, time, location,
  capacity, price, and current registration count
- Register for an event as a signed-in citizen
- Duplicate registrations and full-capacity registrations are handled safely
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
- Open any request to see a progress bar, status timeline, assigned department, and
  assignee
- Dedicated **My Requests** page for each citizen

### Administrative Panel

- Custom admin dashboard at `/admin-dashboard/` for city administrators and
  superusers
- View every service request, who submitted it, and its current status
- Update a service request status without opening the Django admin site
- Review all events and their registration counts
- Route requests to a department from the **Department Dashboard**
- Department managers can update request status and department assignments
- Administrators can manage departments through the Django admin site

Django admin is also configured for managing:

- Users (including the custom role and phone number fields)
- Departments
- Categories
- Events
- Service Requests
- Notifications
- Event Registrations

### User Interface

- Responsive app shell with sidebar navigation and a sticky top bar
- Global search across events and service requests
- Notification dropdown and user profile menu
- City dashboard with key statistics, recent requests, and upcoming events
- Reusable event/request cards, status badges, progress bars, and empty states
- Combined event discovery filter panel with keyword, category, date, location,
  price, and sort controls

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
│   ├── context_processors.py # Notification data for the app shell
│   ├── models.py             # Database models
│   ├── tests.py              # Part 3 regression tests
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
│   │   ├── _messages.html    # Flash message alerts
│   │   ├── _request_card.html  # Reusable request card
│   │   └── _sidebar_nav.html # Sidebar and offcanvas navigation
│   ├── base.html             # Shared layouts, navbar, footer
│   ├── home.html             # Landing page
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── events.html
│   ├── event_detail.html     # Event details and registration
│   ├── submit_request.html
│   ├── my_requests.html
│   ├── admin_dashboard.html  # Admin service request management
│   ├── department_dashboard.html  # Manager request routing and status updates
│   ├── request_detail.html   # Citizen-facing request progress page
│   └── search_results.html   # Global search results
├── db.sqlite3                # Development database
├── manage.py
├── requirements.txt
├── PHASE3_PART2.md           # Part 2 feature guide
├── PHASE3_PART3.md           # Part 3 feature guide
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
| `/events/<id>/` | Event details | Login required |
| `/events/<id>/register/` | Register for an event | Login required |
| `/submit-request/` | Submit a service request | Login required |
| `/my-requests/` | View submitted requests | Login required |
| `/requests/<id>/` | Request progress and details | Owner / assigned worker / manager / admin |
| `/admin-dashboard/` | Custom admin dashboard | City admin / superuser |
| `/department-dashboard/` | Department request routing and status updates | Department manager / city admin / superuser |
| `/search/` | Search events and service requests | Login required |
| `/admin/` | Django admin panel | Staff / superuser |

---

## Usage

### As a Citizen

1. Register an account and sign in.
2. Browse community events on the **Events** page.
3. Search by keyword and combine category, date, location, price, and popularity
   filters.
4. Open an event to see its details and click **Register for this event**.
5. Submit service requests for city issues from **Report Issue**.
6. Follow each request's status on **My Requests**, then click **View progress** for
   the full timeline and department assignment.

### As an Administrator

1. Sign in with an account whose role is **City Administrator**, or with a
   superuser account.
2. Open **Admin Dashboard** from the sidebar or profile menu.
3. Review all service requests and update their status with the dropdown and
   **Update** button.
4. Review all events and see how many citizens registered for each one.
5. Open **Department Dashboard** to route requests to a department and update their
   status.
6. Use `/admin/` when you need full Django admin access for users, departments,
   categories, events, notifications, and registrations.

### As a Department Manager

1. Sign in with an account whose role is **Department Manager**.
2. Open **Departments** from the sidebar or profile menu.
3. Choose the department that should handle a request and set its status.
4. Click **Update** to save the routing and status change.
5. Open a request title to review the citizen-facing progress page.

---

## Data Model

| Model | Purpose |
| --- | --- |
| `User` | Custom authentication user with `role` and `phone_number` fields |
| `Category` | Event category (name and description) |
| `Department` | City department with name, description, contact email, and creation date |
| `Event` | Community event details, organizer, capacity, and price |
| `ServiceRequest` | Citizen issue report with category, department, location, status, and assignee |
| `EventRegistration` | Links a citizen to an event and prevents duplicate registrations |
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
- Event registration, event discovery, request progress tracking, and department
  routing are implemented. Notification delivery and observer-based notifications
  are scheduled for later phases.
- Run `python manage.py test` to execute the Part 3 regression suite.

---

## Roadmap

### Phase III, Part II (complete)

- Event registration system
- Event filtering by category
- Custom admin dashboard for service request status updates

### Phase III, Part III (current)

Implemented in this part:

- Event keyword search and combined category, date, location, price, and
  popularity filters
- Service request progress page with status timeline and access control
- Department model and request-to-department routing
- Department manager dashboard for routing and status updates
- Custom user admin fields for assigning the Department Manager role
- 13 regression tests for the new behavior

Planned for later:

- Observer pattern for notifications
- Factory pattern for service request types
- Admin event creation and editing from the custom dashboard
- Analytics and reporting
- Content moderation
- UI/UX polish

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
