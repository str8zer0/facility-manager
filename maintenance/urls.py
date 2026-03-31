from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    # Work Orders
    path('work-orders/', views.WorkOrderListView.as_view(), name='workorder_list'),
    path('work-orders/create/', views.WorkOrderCreateView.as_view(), name='workorder_create'),
    path('work-orders/<int:pk>/', views.WorkOrderDetailView.as_view(), name='workorder_detail'),
    path('work-orders/<int:pk>/update/', views.WorkOrderUpdateView.as_view(), name='workorder_update'),
    path('work-orders/<int:pk>/delete/', views.WorkOrderDeleteView.as_view(), name='workorder_delete'),
    path('work-orders/<int:pk>/comment/', views.WorkOrderCommentCreateView.as_view(), name='workorder_comment_create'),
    path('work-orders/<int:pk>/attach/', views.WorkOrderAttachmentCreateView.as_view(), name='workorder_attachment_create'),

    # Inspection Templates
    path('templates/', views.InspectionTemplateListView.as_view(), name='inspectiontemplate_list'),
    path('templates/create/', views.InspectionTemplateCreateView.as_view(), name='inspectiontemplate_create'),
    path('templates/<int:pk>/', views.InspectionTemplateDetailView.as_view(), name='inspectiontemplate_detail'),
    path('templates/<int:pk>/update/', views.InspectionTemplateUpdateView.as_view(), name='inspectiontemplate_update'),
    path('templates/<int:pk>/delete/', views.InspectionTemplateDeleteView.as_view(), name='inspectiontemplate_delete'),

    # Inspection Items
    path('templates/<int:template_pk>/items/create/', views.InspectionItemCreateView.as_view(), name='inspectionitem_create'),
    path('items/<int:pk>/update/', views.InspectionItemUpdateView.as_view(), name='inspectionitem_update'),
    path('items/<int:pk>/delete/', views.InspectionItemDeleteView.as_view(), name='inspectionitem_delete'),

    # Inspections
    path('inspections/', views.InspectionListView.as_view(), name='inspection_list'),
    path('inspections/create/', views.InspectionCreateView.as_view(), name='inspection_create'),
    path('inspections/<int:pk>/', views.InspectionDetailView.as_view(), name='inspection_detail'),
    path('inspections/<int:pk>/update/', views.InspectionUpdateView.as_view(), name='inspection_update'),
    path('inspections/<int:pk>/delete/', views.InspectionDeleteView.as_view(), name='inspection_delete'),
    path('inspections/<int:pk>/complete/', views.InspectionCompleteView.as_view(), name='inspection_complete'),
]