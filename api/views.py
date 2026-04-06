from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from assets.models import Asset
from maintenance.models import WorkOrder
from api.serializers import (
    AssetListSerializer, AssetDetailSerializer,
    WorkOrderListSerializer, WorkOrderDetailSerializer,
    WorkOrderCommentSerializer,
)
from api.permissions import IsManagerOrReadOnly, IsOwnerOrManager


# ─────────────────────────────────────────────
# Asset ViewSet
# ─────────────────────────────────────────────

class AssetViewSet(viewsets.ModelViewSet):
    """
    list:   GET  /api/assets/
    create: POST /api/assets/
    retrieve: GET  /api/assets/<id>/
    update: PUT  /api/assets/<id>/
    partial_update: PATCH /api/assets/<id>/
    destroy: DELETE /api/assets/<id>/
    """
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "is_active", "categories"]
    search_fields = ["name", "serial_number", "manufacturer", "model_number"]
    ordering_fields = ["name", "status"]
    ordering = ["name"]

    def get_queryset(self):
        return (
            Asset.objects
            .prefetch_related("categories")
            .select_related("room__building", "assigned_to")
            .all()
        )

    def get_serializer_class(self):
        if self.action == "list":
            return AssetListSerializer
        return AssetDetailSerializer


# ─────────────────────────────────────────────
# WorkOrder ViewSet
# ─────────────────────────────────────────────

class WorkOrderViewSet(viewsets.ModelViewSet):
    """
    list:   GET  /api/work-orders/
    create: POST /api/work-orders/
    retrieve: GET  /api/work-orders/<id>/
    update: PUT  /api/work-orders/<id>/
    partial_update: PATCH /api/work-orders/<id>/
    destroy: DELETE /api/work-orders/<id>/
    comments: GET/POST /api/work-orders/<id>/comments/
    """
    permission_classes = [IsAuthenticated, IsOwnerOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "priority", "is_active", "assigned_to"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "priority", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            WorkOrder.objects
            .select_related("building", "room", "asset", "created_by", "assigned_to")
            .prefetch_related("comments__user")
            .all()
        )

    def get_serializer_class(self):
        if self.action == "list":
            return WorkOrderListSerializer
        return WorkOrderDetailSerializer

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        instance.log(
            user=self.request.user,
            action="Created via API",
            notes=f'Work order "{instance.title}" created via API.',
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.log(
            user=self.request.user,
            action="Updated via API",
            notes=f'Work order "{instance.title}" updated via API.',
        )

    def perform_destroy(self, instance):
        instance.log(
            user=self.request.user,
            action="Deleted via API",
            notes=f'Work order "{instance.title}" deleted via API.',
        )
        instance.delete()

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, *args, **kwargs):
        """
        GET /api/work-orders/<id>/comments/ — list comments
        POST /api/work-orders/<id>/comments/ — add a comment
        """
        work_order = self.get_object()

        if request.method == "GET":
            comments = work_order.comments.select_related("user").all()
            serializer = WorkOrderCommentSerializer(comments, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            serializer = WorkOrderCommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(work_order=work_order, user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return None