from django.urls import path, include
from accounts import views


app_name = "accounts"

dashboard_patterns = [
    path("admin/", views.AdminDashboardView.as_view(), name="dashboard_admin"),
    path("manager/", views.ManagerDashboardView.as_view(), name="dashboard_manager"),
    path("technician/", views.TechnicianDashboardView.as_view(), name="dashboard_technician"),
    path("staff/", views.StaffDashboardView.as_view(), name="dashboard_staff"),
    path("", views.DashboardRouterView.as_view(), name="dashboard"),
]

user_patterns = [
    path("", views.UserListView.as_view(), name="user_list"),
    path("create/", views.UserCreateView.as_view(), name="user_create"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
    path("<int:pk>/edit/", views.UserRoleUpdateView.as_view(), name="user_edit"),
    path("<int:pk>/profile/edit/", views.UserProfileUpdateView.as_view(), name="user_profile_edit"),
    path("<int:pk>/deactivate/", views.UserDeactivateView.as_view(), name="user_deactivate"),
]

department_patterns = [
    path("", views.DepartmentListView.as_view(), name="department_list"),
    path("create/", views.DepartmentCreateView.as_view(), name="department_create"),
    path("<int:pk>/edit/", views.DepartmentUpdateView.as_view(), name="department_edit"),
    path("<int:pk>/delete/", views.DepartmentDeleteView.as_view(), name="department_delete"),
]

job_patterns = [
    path("", views.JobListView.as_view(), name="job_list"),
    path("create/", views.JobCreateView.as_view(), name="job_create"),
    path("<int:pk>/edit/", views.JobUpdateView.as_view(), name="job_edit"),
    path("<int:pk>/delete/", views.JobDeleteView.as_view(), name="job_delete"),
]

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileUpdateView.as_view(), name="profile_edit"),
    path("dashboard/", include(dashboard_patterns)),
    path("users/", include(user_patterns)),
    path("departments/", include(department_patterns)),
    path("jobs/", include(job_patterns)),
]