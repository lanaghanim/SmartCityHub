from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Category,
    Department,
    Event,
    EventRegistration,
    ServiceRequest,
    User,
)


class PartThreeFeatureTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username='adminuser',
            password='test-pass-123',
            role='admin',
            is_staff=True,
            is_superuser=True,
        )
        cls.manager = User.objects.create_user(
            username='manageruser',
            password='test-pass-123',
            role='manager',
        )
        cls.citizen = User.objects.create_user(
            username='citizenuser',
            password='test-pass-123',
            role='citizen',
        )
        cls.other_citizen = User.objects.create_user(
            username='othercitizen',
            password='test-pass-123',
            role='citizen',
        )

        cls.community = Category.objects.create(name='Community')
        cls.environment = Category.objects.create(name='Environment')

        today = timezone.localdate()
        cls.cleanup = Event.objects.create(
            title='Park Cleanup',
            description='Clean the riverside park.',
            date=today + timedelta(days=3),
            time='09:00',
            location='Riverside Park',
            category=cls.environment,
            capacity=20,
            price=Decimal('0.00'),
            organizer=cls.admin,
        )
        cls.workshop = Event.objects.create(
            title='Safety Workshop',
            description='Meet the neighborhood safety team.',
            date=today + timedelta(days=10),
            time='18:00',
            location='Community Hall',
            category=cls.community,
            capacity=20,
            price=Decimal('0.00'),
            organizer=cls.admin,
        )
        cls.festival = Event.objects.create(
            title='City Food Festival',
            description='Local food and music downtown.',
            date=today + timedelta(days=17),
            time='12:00',
            location='Downtown Square',
            category=cls.community,
            capacity=100,
            price=Decimal('12.50'),
            organizer=cls.admin,
        )

        EventRegistration.objects.create(event=cls.cleanup, citizen=cls.citizen)
        EventRegistration.objects.create(event=cls.cleanup, citizen=cls.other_citizen)
        EventRegistration.objects.create(event=cls.workshop, citizen=cls.citizen)

        cls.roads = Department.objects.create(
            name='Roads',
            description='Road repairs and infrastructure.',
            contact_email='roads@example.com',
        )
        cls.lighting = Department.objects.create(
            name='Lighting',
            description='Streetlight maintenance.',
            contact_email='lighting@example.com',
        )
        cls.service_request = ServiceRequest.objects.create(
            title='Pothole on Main Street',
            description='A deep pothole is damaging cars.',
            category='roads',
            department=cls.roads,
            location='Main Street',
            status='open',
            submitted_by=cls.citizen,
        )

    def test_progress_percent_follows_status_order(self):
        self.assertEqual(self.service_request.progress_percent, 20)
        self.service_request.status = 'in_progress'
        self.assertEqual(self.service_request.progress_percent, 60)
        self.service_request.status = 'closed'
        self.assertEqual(self.service_request.progress_percent, 100)

    def test_event_keyword_filter(self):
        self.client.force_login(self.citizen)
        response = self.client.get(reverse('event_list'), {'q': 'riverside'})
        self.assertContains(response, 'Park Cleanup')
        self.assertNotContains(response, 'Safety Workshop')

    def test_event_category_filter(self):
        self.client.force_login(self.citizen)
        response = self.client.get(reverse('event_list'), {'category': 'Environment'})
        self.assertContains(response, 'Park Cleanup')
        self.assertNotContains(response, 'Safety Workshop')

    def test_event_date_filter(self):
        self.client.force_login(self.citizen)
        response = self.client.get(
            reverse('event_list'),
            {'date': self.festival.date.isoformat()},
        )
        self.assertContains(response, 'City Food Festival')
        self.assertNotContains(response, 'Park Cleanup')

    def test_event_price_filter(self):
        self.client.force_login(self.citizen)
        free_response = self.client.get(reverse('event_list'), {'price': 'free'})
        self.assertContains(free_response, 'Park Cleanup')
        self.assertNotContains(free_response, 'City Food Festival')

        paid_response = self.client.get(reverse('event_list'), {'price': 'paid'})
        self.assertContains(paid_response, 'City Food Festival')
        self.assertNotContains(paid_response, 'Park Cleanup')

    def test_event_location_filter(self):
        self.client.force_login(self.citizen)
        response = self.client.get(reverse('event_list'), {'location': 'Riverside'})
        self.assertContains(response, 'Park Cleanup')
        self.assertNotContains(response, 'Safety Workshop')

    def test_event_popularity_sort(self):
        self.client.force_login(self.citizen)
        response = self.client.get(reverse('event_list'), {'sort': 'popular'})
        titles = [event.title for event in response.context['events']]
        self.assertEqual(
            titles,
            ['Park Cleanup', 'Safety Workshop', 'City Food Festival'],
        )

    def test_owner_can_view_request_progress(self):
        self.client.force_login(self.citizen)
        response = self.client.get(
            reverse('request_detail', args=[self.service_request.id]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pothole on Main Street')
        self.assertContains(response, 'Roads')

    def test_other_citizen_cannot_view_request_progress(self):
        self.client.force_login(self.other_citizen)
        response = self.client.get(
            reverse('request_detail', args=[self.service_request.id]),
        )
        self.assertRedirects(response, reverse('my_requests'))

    def test_manager_can_view_and_update_requests(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('department_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pothole on Main Street')

        response = self.client.post(
            reverse('department_dashboard'),
            {
                'request_id': self.service_request.id,
                'status': 'in_progress',
                'department': self.lighting.id,
            },
        )
        self.assertRedirects(response, reverse('department_dashboard'))

        self.service_request.refresh_from_db()
        self.assertEqual(self.service_request.status, 'in_progress')
        self.assertEqual(self.service_request.department, self.lighting)

    def test_citizen_cannot_access_department_dashboard(self):
        self.client.force_login(self.citizen)
        response = self.client.get(reverse('department_dashboard'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_manager_cannot_access_admin_dashboard(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_admin_can_access_admin_dashboard(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Department')
