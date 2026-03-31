from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate, post_save, m2m_changed
from django.dispatch import receiver
from accounts.models import Profile


User = get_user_model()


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """
    Create default user groups (roles) after migrations.
    This runs once after migrate.
    """
    for group_name in settings.ROLE_GROUPS:
        Group.objects.get_or_create(name=group_name)

    if Permission.objects.exists():
        assign_group_permissions()

def assign_group_permissions():
    admin_group = Group.objects.get(name="Admin")
    manager_group = Group.objects.get(name="Manager")
    technician_group = Group.objects.get(name="Technician")
    staff_group = Group.objects.get(name="Staff")

    # Admin → full permissions (but NOT superuser)
    admin_group.permissions.set(Permission.objects.all())

    # Manager → full CRUD except user management
    manager_group.permissions.set(
        Permission.objects.exclude(
            content_type__app_label__in=["auth", "admin", "accounts"]
        )
    )

    # Technician → limited permissions
    technician_group.permissions.set(
        Permission.objects.filter(
            codename__in=[
                # Work Orders
                "view_workorder",
                "change_workorder",
                "add_workordercomment",
                "add_workorderattachment",
                "view_workordercomment",
                "view_workorderattachment",

                # Inspections
                "view_inspection",
                "change_inspection",
                "add_inspectionresult",
                "change_inspectionresult",
                "view_inspectionresult",
                "view_inspectionitem",

                # Assets
                "view_asset",
                "view_assetcategory",

                # Inventory
                "view_sparepart",
                "add_stockmovement",
                "change_stockmovement",
                "view_stockmovement",
            ]
        )
    )

    # Staff → can create work orders, view limited data
    staff_group.permissions.set(
        Permission.objects.filter(
            codename__in=[
                "add_workorder",
                "view_workorder",
                "view_asset",
                "view_room",
            ]
        )
    )


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create default profile for new users.
    This runs whenever a user is created.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()


@receiver(m2m_changed, sender=User.groups.through)
def enforce_staff_status(sender, instance, action, **kwargs):
    """
    Ensure only Admin group users have is_staff=True.
    Everyone else is_staff=False.
    """
    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    admin_group = Group.objects.get(name="Admin")
    is_admin = instance.groups.filter(id=admin_group.id).exists()

    if is_admin and not instance.is_staff:
        instance.is_staff = True
        instance.save(update_fields=["is_staff"])

    if not is_admin and instance.is_staff:
        instance.is_staff = False
        instance.save(update_fields=["is_staff"])
