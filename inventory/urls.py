from django.urls import path
from . import views


app_name = "inventory"

urlpatterns = [
    path("suppliers/", views.SupplierListView.as_view(), name="supplier_list"),
    path("suppliers/create/", views.SupplierCreateView.as_view(), name="supplier_create"),
    path("suppliers/<int:pk>/", views.SupplierDetailView.as_view(), name="supplier_detail"),
    path("suppliers/<int:pk>/edit/", views.SupplierUpdateView.as_view(), name="supplier_edit"),
    path("suppliers/<int:pk>/delete/", views.SupplierDeleteView.as_view(), name="supplier_delete"),

    path("parts/", views.SparePartListView.as_view(), name="sparepart_list"),
    path("parts/create/", views.SparePartCreateView.as_view(), name="sparepart_create"),
    path("parts/<int:pk>/", views.SparePartDetailView.as_view(), name="sparepart_detail"),
    path("parts/<int:pk>/edit/", views.SparePartUpdateView.as_view(), name="sparepart_edit"),
    path("parts/<int:pk>/delete/", views.SparePartDeleteView.as_view(), name="sparepart_delete"),
    path("parts/<int:part_pk>/log/", views.StockMovementCreateView.as_view(), name="movement_create"),

    path("movements/", views.StockMovementListView.as_view(), name="movement_list")
]