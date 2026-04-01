from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('work-orders/', views.WorkOrderListView.as_view(), name='workorder_list'),
    path('work-orders/create/', views.WorkOrderCreateView.as_view(), name='workorder_create'),
    path('work-orders/<int:pk>/', views.WorkOrderDetailView.as_view(), name='workorder_detail'),
    path('work-orders/<int:pk>/update/', views.WorkOrderUpdateView.as_view(), name='workorder_update'),
    path('work-orders/<int:pk>/delete/', views.WorkOrderDeleteView.as_view(), name='workorder_delete'),
    path('work-orders/<int:pk>/comments/add/', views.WorkOrderCommentCreateView.as_view(), name='workorder_comment_add'),

    path('inspections/', views.InspectionListView.as_view(), name='inspection_list'),
    path('inspections/create/', views.InspectionCreateView.as_view(), name='inspection_create'),
    path('inspections/<int:pk>/', views.InspectionDetailView.as_view(), name='inspection_detail'),
    path('inspections/<int:pk>/update/', views.InspectionUpdateView.as_view(), name='inspection_update'),
    path('inspections/<int:pk>/delete/', views.InspectionDeleteView.as_view(), name='inspection_delete'),
]