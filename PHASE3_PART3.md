# Phase III, Part 3 - Implemented Features

This document is the quick guide for the Phase III, Part 3 submission. It explains
the new features added on top of Parts 1 and 2, where to find them, and how to test
them.

**Repository:** [github.com/lanaghanim/SmartCityHub](https://github.com/lanaghanim/SmartCityHub)  
**Branch:** `phase3-part3`

---

## What Was Added in This Part

| Feature | What it does | Where to find it | Status |
| --- | --- | --- | --- |
| Event discovery | Search events by keyword and filter by category, date, location, free/paid price, and popularity. | `/events/` | Implemented |
| Request progress tracking | Citizens can open a request and see a progress bar, status timeline, assigned department, assignee, and update times. | `/my-requests/` and `/requests/<id>/` | Implemented |
| Department operations | A new `Department` model and `ServiceRequest.department` field let managers route requests and update their status. | `/department-dashboard/` | Implemented |
| Department admin | Departments are registered in Django admin, and the user form exposes the custom role field so an administrator can create Department Managers. | `/admin/` | Implemented |
| Regression tests | 13 automated tests cover event filters, request access rules, and department dashboard updates. | `core/tests.py` | Implemented |

---

## 1. Event Discovery

The Events page now has a combined discovery panel instead of the category-only
filter from Part 2.

What the feature includes:

- **Keyword search** across event title, description, location, and category name.
- **Category filter** populated from the `Category` model.
- **Exact date filter** using an HTML date input.
- **Location filter** with a case-insensitive partial match.
- **Price filter** for free events and paid events.
- **Popularity sort** that orders events by registration count, then by date.
- Filters can be combined. The selected values stay visible in the form after the
  page reloads.
- A **Clear filters** button appears whenever at least one filter is active.
- A result count is shown when filters are active.
- Event cards show registered count vs. capacity.

**Query parameters:**

| Parameter | Example | Meaning |
| --- | --- | --- |
| `q` | `?q=park` | Keyword search |
| `category` | `?category=Environment` | Category name |
| `date` | `?date=2026-12-12` | Exact event date |
| `location` | `?location=Riverside` | Location substring |
| `price` | `?price=free` or `?price=paid` | Price type |
| `sort` | `?sort=popular` | Most registrations first |

**Code locations:**

- View: `core/views.py` - `event_list`
- Template: `templates/events.html`
- Event card: `templates/partials/_event_card.html`
- Styling: `static/css/style.css` - `.filter-card`

---

## 2. Service Request Progress Tracking

Citizens can now follow a request from submission to resolution.

What the feature includes:

- A **View progress** button on every request card.
- A request detail page at `/requests/<id>/` with:
  - A status badge.
  - A progress bar whose fill follows the request status.
  - A timeline with all five stages: Open, Assigned, In Progress, Resolved, Closed.
  - The assigned department.
  - The assigned worker, if any.
  - The submitter, location, submission time, and last update time.
  - The full request description.
- Dashboard request titles link directly to the progress page.
- Access is limited to:
  - The citizen who submitted the request.
  - The user assigned to the request.
  - Department managers.
  - City administrators, staff, and superusers.
- Other citizens are redirected to **My Requests** with an access-denied message.

**Status progress values:**

| Status | Progress |
| --- | --- |
| Open | 20% |
| Assigned | 40% |
| In Progress | 60% |
| Resolved | 80% |
| Closed | 100% |

**Code locations:**

- Model property: `core/models.py` - `ServiceRequest.progress_percent`
- View: `core/views.py` - `request_detail`
- URL: `core/urls.py` - `request_detail`
- Template: `templates/request_detail.html`
- Card: `templates/partials/_request_card.html`
- Styling: `static/css/style.css` - `.request-progress`, `.request-timeline`

---

## 3. Department Operations

City departments are now first-class records, and service requests can be routed to
them.

What the feature includes:

- A new `Department` model with:
  - `name`
  - `description`
  - `contact_email`
  - `created_at`
- A new nullable `ServiceRequest.department` foreign key with
  `on_delete=SET_NULL`.
- A department manager dashboard at `/department-dashboard/`.
- The dashboard lists every service request with:
  - Request ID and title.
  - Submitter.
  - Category.
  - Current department.
  - Current status.
- Each row has a department dropdown and a status dropdown.
- Clicking **Update** saves both fields in one POST request with CSRF protection.
- An empty department choice unassigns the request.
- Invalid status values are rejected without changing the request.
- Access is restricted to users with the **Department Manager** role, the
  **City Administrator** role, or superuser status.
- Citizens are redirected to their dashboard with an access-denied message.
- Managers and administrators get **Departments** links in the sidebar and profile
  menu.
- Administrators can open the Django admin site to create departments and edit a
  user's role.

**Code locations:**

- Models: `core/models.py` - `Department`, `ServiceRequest.department`
- Migration: `core/migrations/0003_department_servicerequest_department.py`
- Views: `core/views.py` - `department_dashboard`, `request_detail`
- URL: `core/urls.py` - `department_dashboard`
- Template: `templates/department_dashboard.html`
- Navigation: `templates/partials/_sidebar_nav.html`, `templates/base.html`
- Admin: `core/admin.py` - `SmartCityUserAdmin`, `Department`

---

## Data Model Change

```python
class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.name


class ServiceRequest(models.Model):
    # ... existing fields ...
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_requests',
    )

    @property
    def progress_percent(self):
        statuses = [value for value, _ in self.STATUS_CHOICES]
        index = statuses.index(self.status) if self.status in statuses else 0
        return round((index + 1) / len(statuses) * 100)
```

The `Department` model is registered in `core/admin.py`. The custom user admin now
adds the `role` and `phone_number` fields to the user edit and create forms, so a
superuser can promote an account to **Department Manager** from `/admin/`.

---

## Routes Added or Updated

| URL | Page | Access |
| --- | --- | --- |
| `/events/` | Event discovery with search and combined filters | Login required |
| `/my-requests/` | Request cards with **View progress** links | Login required |
| `/requests/<id>/` | Request progress and details | Owner / assigned worker / manager / admin |
| `/department-dashboard/` | Department request routing and status updates | Department manager / city admin / superuser |
| `/admin-dashboard/` | Admin dashboard, now with department column and request links | City admin / superuser |
| `/admin/` | Django admin for departments, users, and roles | Staff / superuser |

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

### 2. Test event discovery

1. Sign in as a citizen.
2. Open **Events**.
3. Enter `park` in **Keyword** and apply the filters. Confirm only matching events
   are shown.
4. Choose `Environment` in **Category** and confirm only environment events remain.
5. Pick an event date in **Date** and confirm only that date is shown.
6. Enter `Riverside` in **Location** and confirm only Riverside events are shown.
7. Choose **Free** and then **Paid** in **Price** and confirm the results change.
8. Choose **Most popular** in **Sort by** and confirm the event with the most
   registrations appears first.
9. Click **Clear filters** and confirm the full upcoming event list returns.

### 3. Test request progress

1. Sign in as a citizen and submit a service request from **Report an issue**.
2. Open **My Requests**.
3. Click **View progress** on the new request.
4. Confirm the status badge, progress bar, timeline, department, and update times
   are shown.
5. Sign in as a different citizen and try to open the same `/requests/<id>/` URL.
   Confirm the page redirects to **My Requests** with an access-denied message.

### 4. Test the department manager dashboard

1. Sign in as a user whose role is **Department Manager**.
2. Open **Departments** from the sidebar or profile menu.
3. Confirm every service request is listed with its current department and status.
4. Select a department and a new status for one request.
5. Click **Update**.
6. Confirm the success message and the updated department and status badges.
7. Open the request title and confirm the citizen-facing progress page reflects the
   new status and department.
8. Sign in as a citizen and confirm `/department-dashboard/` redirects away with an
   access-denied message.

### 5. Test the admin tools

1. Sign in as a superuser and open `/admin/`.
2. Open **Departments** and confirm the department records are listed.
3. Open **Users**, edit a user, and confirm the **SmartCity Hub** section exposes
   the role and phone number fields.
4. Set a user's role to **Department Manager** and confirm that account can open
   `/department-dashboard/`.

---

## Verification

The following checks were run after implementing the features:

- `python manage.py check` - no issues.
- `python manage.py test -v 2` - 13 tests passed.
- Manual smoke tests covering:
  - Keyword, category, date, location, free/paid, and popularity event filters.
  - Request progress rendering and owner access.
  - Access denial for a different citizen.
  - Department manager dashboard access and request updates.
  - Invalid status rejection.
  - Admin dashboard access and manager access denial.
  - Sidebar link visibility for managers and administrators.
  - Search, dashboard, and public pages.

The test suite is in `core/tests.py`.

---

## Related Documentation

- [README.md](README.md) - project overview, setup, routes, and data model
- [PHASE3_PART2.md](PHASE3_PART2.md) - Phase III, Part 2 feature guide
- [Phase III, Part 3 branch](https://github.com/lanaghanim/SmartCityHub/tree/phase3-part3)
