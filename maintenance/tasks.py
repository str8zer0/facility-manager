from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_technician_assigned(self, work_order_id):
    """
    Send an email to a technician when a work order is assigned to them.
    Triggered from WorkOrderCreateView and WorkOrderUpdateView.
    """
    try:
        from maintenance.models import WorkOrder
        work_order = WorkOrder.objects.select_related(
            "assigned_to", "building", "room", "asset"
        ).get(pk=work_order_id)

        if not work_order.assigned_to:
            return

        technician = work_order.assigned_to
        if not technician.email:
            return

        subject = f"Work Order Assigned: {work_order.title}"
        message = f"""
Hi {technician.email},

A work order has been assigned to you.

Title:    {work_order.title}
Priority: {work_order.get_priority_display()}
Status:   {work_order.get_status_display()}
Location: {work_order.location}
Due Date: {work_order.due_date or "Not set"}

Please log in to the Facility Manager to view the full details.

This is an automated notification.
        """.strip()

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[technician.email],
            fail_silently=False,
        )

    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_work_order_status_changed(self, work_order_id, old_status, new_status):
    """
    Send an email notification when a work order status changes.
    Notifies both the creator and the assigned technician.
    Triggered from WorkOrderUpdateView.
    """
    try:
        from maintenance.models import WorkOrder
        work_order = WorkOrder.objects.select_related(
            "created_by", "assigned_to"
        ).get(pk=work_order_id)

        recipients = []

        if work_order.created_by and work_order.created_by.email:
            recipients.append(work_order.created_by.email)

        if (
            work_order.assigned_to and
            work_order.assigned_to.email and
            work_order.assigned_to.email not in recipients
        ):
            recipients.append(work_order.assigned_to.email)

        if not recipients:
            return

        subject = f"Work Order Status Update: {work_order.title}"
        message = f"""
Hi,

The status of a work order has been updated.

Title:      {work_order.title}
Location:   {work_order.location}
Old Status: {old_status}
New Status: {new_status}

Please log in to the Facility Manager to view the full details.

This is an automated notification.
        """.strip()

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )

    except Exception as exc:
        raise self.retry(exc=exc)