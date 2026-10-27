from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect


from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user  # Get current user

        # ✅ Allow home page and login-related views
        allowed_paths = [
            reverse('home'),  # Home page
            reverse('login_page'),  # Login page
            reverse('user_login'),  # Custom login view
            reverse('invoicing_webhook'),  # Webhook from invoicing system should be allowed without session
        ]

        if request.path in allowed_paths or modulename == 'django.contrib.auth.views':
            return None  # Allow access

        if user.is_authenticated:
            if user.user_type == 1:  # HOD
                if modulename in ['main_app.student_views']:
                    return redirect(reverse('admin_home'))
            elif user.user_type == 2:  # Staff
                if modulename in ['main_app.student_views', 'main_app.hod_views']:
                    return redirect(reverse('staff_home'))
            elif user.user_type == 3:  # Student
                if modulename in ['main_app.hod_views', 'main_app.staff_views']:
                    return redirect(reverse('student_home'))
            return None
        else:
            # 🔥 Fix: Allow unauthenticated users to access the home page!
            if request.path not in allowed_paths:
                return redirect(reverse('login_page'))
