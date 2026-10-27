import json
from django.test import TestCase, Client
from django.conf import settings


class InvoicingWebhookTests(TestCase):
	def setUp(self):
		from .models import CustomUser

		# ensure there is an API key available for the tests
		if not getattr(settings, 'INVOICING_API_KEY', None):
			settings.INVOICING_API_KEY = 'test-invoicing-key'

		# create a student user (post_save signal will create Student)
		self.user = CustomUser.objects.create_user(
			email='test.student@example', password='password', user_type=3,
			first_name='Test', last_name='Student', profile_pic=''
		)
		self.user.save()
		self.student = self.user.student
		self.student.registration_number = 'TEST-REG-001'
		self.student.save()

	def test_webhook_with_valid_api_key_creates_notification(self):
		from .models import NotificationStudent

		c = Client()
		payload = {
			'registration_number': 'TEST-REG-001',
			'invoice_id': 11,
			'amount_paid': 20000,
			'receipt_date': '2026-08-14'
		}
		resp = c.post('/webhooks/invoicing/', data=json.dumps(payload), content_type='application/json', HTTP_X_API_KEY=settings.INVOICING_API_KEY)
		self.assertEqual(resp.status_code, 200)
		note = NotificationStudent.objects.filter(student=self.student).order_by('-created_at').first()
		self.assertIsNotNone(note)
		# message should be the payload JSON (view uses payload.get('message') or json.dumps(payload))
		self.assertIn('TEST-REG-001', note.message)

	def test_webhook_with_invalid_api_key_is_forbidden(self):
		from .models import NotificationStudent

		c = Client()
		payload = {
			'registration_number': 'TEST-REG-001',
			'invoice_id': 11,
			'amount_paid': 20000,
			'receipt_date': '2026-08-14'
		}
		resp = c.post('/webhooks/invoicing/', data=json.dumps(payload), content_type='application/json', HTTP_X_API_KEY='BAD_KEY')
		self.assertEqual(resp.status_code, 403)
		# ensure no new notification was created by the bad request
		notes = NotificationStudent.objects.filter(student=self.student)
		# there should be zero notifications (or only those created by other tests in this run) -- ensure none match this payload
		self.assertFalse(notes.filter(message__icontains='invoice_id').exists())


class SSOTests(TestCase):
	def setUp(self):
		from .models import CustomUser

		# create HOD and Staff users
		self.hod = CustomUser.objects.create_user(email='hod2@example', password='pwd', user_type=1, first_name='Hod', last_name='User', profile_pic='')
		self.hod.set_password('pwd')
		self.hod.save()

		self.staff = CustomUser.objects.create_user(email='staff2@example', password='pwd', user_type=2, first_name='Staff', last_name='User', profile_pic='')
		self.staff.set_password('pwd')
		self.staff.save()

	def test_hod_gets_sso_token_redirect(self):
		c = Client()
		c.force_login(self.hod)
		resp = c.get('/accounting/sso/', follow=False)
		self.assertEqual(resp.status_code, 302)
		loc = resp.get('Location')
		self.assertIn('/sso-login/?token=', loc)

	def test_staff_does_not_get_token(self):
		c = Client()
		c.force_login(self.staff)
		resp = c.get('/accounting/sso/', follow=False)
		self.assertEqual(resp.status_code, 302)
		loc = resp.get('Location')
		# staff should be routed to staff_home, not given a token
		self.assertNotIn('/sso-login/?token=', loc)

	def test_unauthenticated_redirects_to_login(self):
		c = Client()
		resp = c.get('/accounting/sso/', follow=False)
		self.assertEqual(resp.status_code, 302)
		self.assertIn('/login', resp.get('Location'))


class StudentResultsPortalTests(TestCase):
	def setUp(self):
		from .models import Course, CustomUser, Student, StudentResult, Subject

		self.course = Course.objects.create(name='Results Test Course')
		self.student_user = CustomUser.objects.create_user(
			email='results.student@example', password='password', user_type=3,
			first_name='Results', last_name='Student', profile_pic=''
		)
		self.student = Student.objects.get(admin=self.student_user)
		self.other_student_user = CustomUser.objects.create_user(
			email='other.results.student@example', password='password', user_type=3,
			first_name='Other', last_name='Student', profile_pic=''
		)
		self.other_student = Student.objects.get(admin=self.other_student_user)
		self.staff_user = CustomUser.objects.create_user(
			email='results.staff@example', password='password', user_type=2,
			first_name='Results', last_name='Staff', profile_pic=''
		)
		self.subject = Subject.objects.create(
			name='Results Test Subject', course=self.course,
			staff=self.staff_user.staff
		)
		StudentResult.objects.create(
			student=self.student, subject=self.subject, test=23, exam=54
		)
		StudentResult.objects.create(
			student=self.other_student, subject=self.subject, test=91, exam=92
		)

	def test_student_can_view_only_own_results_without_download_controls(self):
		self.client.force_login(self.student_user)

		response = self.client.get('/student/view/result/')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Results Test Subject')
		self.assertContains(response, '23.0')
		self.assertContains(response, '54.0')
		self.assertContains(response, '77.0')
		self.assertNotContains(response, '91.0')
		self.assertNotContains(response, '92.0')
		page = response.content.lower()
		self.assertNotIn(b'download', page)
		self.assertNotIn(b'.pdf', page)

	def test_student_cannot_access_results_download_url(self):
		self.client.force_login(self.student_user)

		response = self.client.get('/student/view/result/download/')

		self.assertEqual(response.status_code, 404)

	def test_staff_result_entry_remains_available(self):
		from .models import StudentResult

		self.client.force_login(self.staff_user)

		response = self.client.post('/staff/result/add/', {
			'student_list': self.student.pk,
			'subject': self.subject.pk,
			'test': '30',
			'exam': '60',
		})

		self.assertEqual(response.status_code, 200)
		result = StudentResult.objects.get(student=self.student, subject=self.subject)
		self.assertEqual(result.test, 30)
		self.assertEqual(result.exam, 60)

