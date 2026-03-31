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

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileUpdateView.as_view(), name="profile_edit"),
    path("dashboard/", include(dashboard_patterns)),
]