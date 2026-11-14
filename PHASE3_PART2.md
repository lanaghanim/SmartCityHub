# Phase III, Part 2 - Implemented Features

This document is the quick guide for the Phase III, Part 2 submission. It explains
the three new features added on top of Part 1, where to find them, and how to test
them.

**Repository:** [github.com/lanaghanim/SmartCityHub](https://github.com/lanaghanim/SmartCityHub)  
**Branch:** `phase3-part2`

---

## What Was Added in This Part

| Feature | What it does | Where to find it | Status |
| --- | --- | --- | --- |
| Event registration | Citizens can view an event and register for it. Duplicate, full-capacity, and past-event registrations are blocked. | `/events/<id>/` and `/events/<id>/register/` | Implemented |
| Event filtering | Citizens can filter the Events page by category using a dropdown. | `/events/` | Implemented |
| Admin dashboard | City administrators and superusers can view all service requests, update their status, and review event registration counts. | `/admin-dashboard/` | Implemented |

---

## Feature Screenshots

### Event filtering
![Events page with the category filter](<project_ui/citizens events page.png>)

### Event registration
![Event details after successful registration](<project_ui/event details you are registered.png>)

### Admin access
![Admin dashboard navigation and admin links](<project_ui/admin dashboard.png>)

### Django admin panel
![Django admin panel with Event Registrations](<project_ui/admin panel.png>)

---

## 1. Event Registration

Citizens can now open an event detail page and register for it.

What the feature includes:

- A new `EventRegistration` model that links one citizen to one event.
- A database-level unique constraint so the same citizen cannot register twice for
  the same event.
- An event detail page showing the event description, date, time, location, price,
  capacity, and current registration count.
- A **Register for this event** button.
- A success message after registering and a warning for duplicate registrations.
- A capacity check that stops registrations once the event is full.
- A date check that stops registrations for events that have already happened.

**Code locations:**

- Model: `core/models.py` - `EventRegistration`
- Migration: `core/migrations/0002_eventregistration.py`
- Views: `core/views.py` - `event_detail`, `register_for_event`
- URLs: `core/urls.py` - `event_detail`, `register_for_event`
- Templates: `templates/event_detail.html`, `templates/partials/_event_card.html`

---

## 2. Event Filtering by Category

The Events page now has a category dropdown above the event cards.

What the feature includes:

- A **Filter by category** dropdown populated from the `Category` model.
- The selected category is applied through the `?category=` query parameter.
- A **Clear filter** link appears when a category is selected.
- The filter works together with the existing rule that only upcoming events are
  shown on the Events page.

**Code locations:**

- View: `core/views.py` - `event_list`
- Template: `templates/events.html`
- Styling: `static/css/style.css` - `.event-filter`

---

## 3. Admin Dashboard

City administrators and superusers now have a custom dashboard that does not require
the Django admin site for everyday service request work.

What the feature includes:

- Access is restricted to users with the **City Administrator** role or superuser
  status.
- A list of every service request with its ID, title, location, submitter, category,
  and current status.
- A status dropdown and **Update** button on every request row.
- Status updates use a POST request with CSRF protection and redirect back to the
  dashboard after saving.
- A list of all events with their date, category, location, and registration count.
- Sidebar and profile-menu links for administrators.

**Code locations:**

- View: `core/views.py` - `admin_dashboard`
- URL: `core/urls.py` - `admin_dashboard`
- Template: `templates/admin_dashboard.html`
- Navigation: `templates/partials/_sidebar_nav.html`, `templates/base.html`

---

## How to Test the Features

### 1. Run the project

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

### 2. Test event filtering

1. Sign in as a citizen.
2. Open **Events**.
3. Choose a category from the **Filter by category** dropdown.
4. Confirm that only events in that category are shown.
5. Click **Clear filter** to see all upcoming events again.

### 3. Test event registration

1. On the Events page, click **View details** on an event.
2. Confirm the event details and registration count are shown.
3. Click **Register for this event**.
4. Confirm the success message and the **You are registered** badge.
5. Open the register URL again and confirm a duplicate registration is blocked.
6. Try an event with `capacity = 1` and register a second citizen. The second
   registration should show a full-capacity message.
7. Try registering for an event whose date is in the past. It should be blocked.

### 4. Test the admin dashboard

1. Sign in with the superuser account, or an account whose role is
   **City Administrator**.
2. Open **Admin Dashboard** from the sidebar or profile menu.
3. Confirm all service requests are listed.
4. Change one request's status and click **Update**.
5. Confirm the success message and the updated status badge.
6. Confirm the event list shows registration counts.
7. Sign in as a normal citizen and confirm `/admin-dashboard/` redirects away with
   an access-denied message.

---

## Data Model Change

```python
class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    citizen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['event', 'citizen'],
                name='unique_event_registration',
            ),
        ]
```

The model is also registered in `core/admin.py`, so registrations can be managed
through the Django admin site.

---

## Verification

The following checks were run after implementing the features:

- `python manage.py check`
- `python manage.py test` (the project test suite is still a placeholder, so 0 tests ran)
- Smoke tests covering:
  - Event category filtering
  - Event detail rendering
  - Successful registration
  - Duplicate registration prevention
  - Full-capacity prevention
  - Past-event prevention
  - Admin-only dashboard access
  - Service request status updates
  - Dashboard, search, and public pages

---

## Related Documentation

- [README.md](README.md) - project overview, setup, routes, and data model
- [Phase III, Part 2 branch](https://github.com/lanaghanim/SmartCityHub/tree/phase3-part2)
