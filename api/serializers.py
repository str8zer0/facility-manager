from rest_framework import serializers
from assets.models import Asset, AssetCategory
from maintenance.models import WorkOrder, WorkOrderComment
from accounts.models import User


# ─────────────────────────────────────────────
# Asset Serializers
# ─────────────────────────────────────────────

class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = ["id", "name"]


class AssetListSerializer(serializers.ModelSerializer):
    categories = AssetCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=AssetCategory.objects.all(),
        source="categories",
        write_only=True,
        required=False
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    room = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Asset
        fields = [
            "id", "name", "categories", "category_ids", "room",
            "status", "status_display", "is_active",
        ]


class AssetDetailSerializer(serializers.ModelSerializer):
    categories = AssetCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=AssetCategory.objects.all(),
        source="categories",
        write_only=True,
        required=False
    )
    room = serializers.StringRelatedField(read_only=True)
    room_id = serializers.IntegerField(source="room.id", read_only=True)
    assigned_to = serializers.StringRelatedField(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source="assigned_to",
        write_only=True,
        required=False,
        allow_null=True,
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Asset
        fields = [
            "id", "name",
            "categories", "category_ids",
            "room", "room_id",
            "status", "status_display",
            "serial_number", "manufacturer", "model_number",
            "purchase_date", "installation_date", "warranty_expiration",
            "assigned_to", "assigned_to_id",
            "is_active", "notes",
        ]


# ─────────────────────────────────────────────
# WorkOrder Serializers
# ─────────────────────────────────────────────

class WorkOrderCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = WorkOrderComment
        fields = ["id", "user", "comment", "timestamp"]
        read_only_fields = ["user", "timestamp"]


class WorkOrderListSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    assigned_to = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    location = serializers.CharField(read_only=True)

    class Meta:
        model = WorkOrder
        fields = [
            "id", "title", "status", "status_display",
            "priority", "priority_display", "location",
            "created_by", "assigned_to", "due_date", "created_at",
        ]


class WorkOrderDetailSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    assigned_to = serializers.StringRelatedField(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source="assigned_to",
        write_only=True,
        required=False,
        allow_null=True,
    )
    building = serializers.StringRelatedField(read_only=True)
    building_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    room = serializers.StringRelatedField(read_only=True)
    room_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    asset = serializers.StringRelatedField(read_only=True)
    asset_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    location = serializers.CharField(read_only=True)
    comments = WorkOrderCommentSerializer(many=True, read_only=True)

    class Meta:
        model = WorkOrder
        fields = [
            "id", "title", "description",
            "building", "building_id",
            "room", "room_id",
            "asset", "asset_id",
            "status", "status_display",
            "priority", "priority_display",
            "location",
            "created_by", "assigned_to", "assigned_to_id",
            "due_date", "created_at", "updated_at",
            "is_active", "comments",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]

    def validate(self, data):
        building_id = data.get("building_id") or (self.instance.building_id if self.instance else None)
        room_id = data.get("room_id") or (self.instance.room_id if self.instance else None)
        asset_id = data.get("asset_id") or (self.instance.asset_id if self.instance else None)

        if not any([building_id, room_id, asset_id]):
            raise serializers.ValidationError(
                "A work order must reference at least a building, room, or asset."
            )
        return data