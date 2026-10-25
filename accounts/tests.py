from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Department, Profile


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name='Computer Science', code='CSE')

        # Admin user
        self.admin_user = User.objects.create_user(username='admin_test', password='password123')
        Profile.objects.create(user=self.admin_user, role=Profile.ROLE_ADMIN)

        # HOD user
        self.hod_user = User.objects.create_user(username='hod_test', password='password123')
        Profile.objects.create(user=self.hod_user, role=Profile.ROLE_HOD, department=self.dept)

        # Faculty user
        self.faculty_user = User.objects.create_user(username='faculty_test', password='password123')
        Profile.objects.create(user=self.faculty_user, role=Profile.ROLE_FACULTY, department=self.dept)

        # Inactive user
        self.inactive_user = User.objects.create_user(username='inactive_test', password='password123', is_active=False)
        Profile.objects.create(user=self.inactive_user, role=Profile.ROLE_FACULTY, department=self.dept)

    def test_valid_login_redirects_to_role_dashboard(self):
        """Valid login should authenticate and direct user based on role."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'admin_test',
            'password': 'password123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        # Should be directed to admin dashboard
        self.assertTemplateUsed(response, 'accounts/dashboard_admin.html')

    def test_invalid_login_fails(self):
        """Invalid credentials should re-render login with error."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'admin_test',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertFormError(response, 'form', None, "Please enter a correct username and password. Note that both fields may be case-sensitive.")

    def test_inactive_user_cannot_login(self):
        """Inactive user credentials should be rejected."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'inactive_test',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_logout_post_required(self):
        """Logout must be a POST request; GET request does not log out."""
        self.client.login(username='hod_test', password='password123')

        # GET request should not log user out
        get_response = self.client.get(reverse('accounts:logout'), follow=True)
        self.assertTrue(get_response.context['user'].is_authenticated)

        # POST request logs out
        post_response = self.client.post(reverse('accounts:logout'), follow=True)
        self.assertFalse(post_response.context['user'].is_authenticated)
        self.assertRedirects(post_response, reverse('accounts:login'))

    def test_role_based_dashboard_routing(self):
        """HOD and Faculty should route to their respective dashboards."""
        # Test HOD
        self.client.login(username='hod_test', password='password123')
        resp_hod = self.client.get(reverse('accounts:dashboard'), follow=True)
        self.assertTemplateUsed(resp_hod, 'accounts/dashboard_hod.html')
        self.client.logout()

        # Test Faculty
        self.client.login(username='faculty_test', password='password123')
        resp_fac = self.client.get(reverse('accounts:dashboard'), follow=True)
        self.assertTemplateUsed(resp_fac, 'accounts/dashboard_faculty.html')


class RBACTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept_cse = Department.objects.create(name='Computer Science', code='CSE')
        self.dept_ece = Department.objects.create(name='Electronics', code='ECE')

        self.admin = User.objects.create_user(username='admin_u', password='password123')
        Profile.objects.create(user=self.admin, role=Profile.ROLE_ADMIN)

        self.hod_cse = User.objects.create_user(username='hod_cse_u', password='password123')
        Profile.objects.create(user=self.hod_cse, role=Profile.ROLE_HOD, department=self.dept_cse)

        self.faculty_cse = User.objects.create_user(username='fac_cse_u', password='password123')
        Profile.objects.create(user=self.faculty_cse, role=Profile.ROLE_FACULTY, department=self.dept_cse)

        self.faculty_ece = User.objects.create_user(username='fac_ece_u', password='password123')
        Profile.objects.create(user=self.faculty_ece, role=Profile.ROLE_FACULTY, department=self.dept_ece)

    def test_admin_dashboard_rbac(self):
        """Only Admin can access admin dashboard; HOD and Faculty are forbidden (403)."""
        # HOD forbidden
        self.client.login(username='hod_cse_u', password='password123')
        resp_hod = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(resp_hod.status_code, 403)
        self.client.logout()

        # Faculty forbidden
        self.client.login(username='fac_cse_u', password='password123')
        resp_fac = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(resp_fac.status_code, 403)
        self.client.logout()

        # Admin allowed
        self.client.login(username='admin_u', password='password123')
        resp_adm = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(resp_adm.status_code, 200)

    def test_admin_toggle_user_active(self):
        """Admin can toggle user active status but cannot deactivate self."""
        self.client.login(username='admin_u', password='password123')

        # Toggle faculty status to inactive
        self.assertTrue(self.faculty_cse.is_active)
        self.client.post(reverse('accounts:toggle_user_active', args=[self.faculty_cse.id]))
        self.faculty_cse.refresh_from_db()
        self.assertFalse(self.faculty_cse.is_active)

        # Toggle back to active
        self.client.post(reverse('accounts:toggle_user_active', args=[self.faculty_cse.id]))
        self.faculty_cse.refresh_from_db()
        self.assertTrue(self.faculty_cse.is_active)

        # Admin cannot toggle own status
        self.client.post(reverse('accounts:toggle_user_active', args=[self.admin.id]))
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_hod_department_isolation_faculty_management(self):
        """HOD cannot remove faculty belonging to another department."""
        self.client.login(username='hod_cse_u', password='password123')

        # Attempt to remove faculty from ECE department
        self.client.post(reverse('accounts:remove_faculty', args=[self.faculty_ece.id]))
        self.faculty_ece.refresh_from_db()
        self.assertTrue(self.faculty_ece.is_active)  # Remains active
