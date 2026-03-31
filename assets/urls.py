from django.urls import path
from assets import views


app_name = "assets"

urlpatterns = [
    path("categories/", views.AssetCategoryListView.as_view(), name="category_list"),
    path("categories/create/", views.AssetCategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", views.AssetCategoryUpdateView.as_view(), name="category_edit"),
    path("categories/<int:pk>/delete/", views.AssetCategoryDeleteView.as_view(), name="category_delete"),

    path("", views.AssetListView.as_view(), name="asset_list"),
    path("create/", views.AssetCreateView.as_view(), name="asset_create"),
    path("<int:pk>/", views.AssetDetailView.as_view(), name="asset_detail"),
    path("<int:pk>/edit/", views.AssetUpdateView.as_view(), name="asset_edit"),
    path("<int:pk>/delete/", views.AssetDeleteView.as_view(), name="asset_delete"),
]