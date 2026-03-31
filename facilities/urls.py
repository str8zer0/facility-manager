from django.urls import path
from facilities import views


app_name = "facilities"

urlpatterns = [
    path("buildings/", views.BuildingListView.as_view(), name="building_list"),
    path("buildings/create/", views.BuildingCreateView.as_view(), name="building_create"),
    path("buildings/<int:pk>/", views.BuildingDetailView.as_view(), name="building_detail"),
    path("buildings/<int:pk>/edit/", views.BuildingUpdateView.as_view(), name="building_edit"),
    path("buildings/<int:pk>/delete/", views.BuildingDeleteView.as_view(), name="building_delete"),

    path("rooms/", views.RoomListView.as_view(), name="room_list"),
    path("rooms/create/", views.RoomCreateView.as_view(), name="room_create"),
    path("rooms/<int:pk>/", views.RoomDetailView.as_view(), name="room_detail"),
    path("rooms/<int:pk>/edit/", views.RoomUpdateView.as_view(), name="room_edit"),
    path("rooms/<int:pk>/delete/", views.RoomDeleteView.as_view(), name="room_delete"),
]