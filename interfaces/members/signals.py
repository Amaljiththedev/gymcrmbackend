from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from interfaces.members.models import Member, PaymentHistory


@receiver(pre_save, sender=Member)
def capture_old_member_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_membership_plan_id = old_instance.membership_plan_id
            instance._old_membership_start = old_instance.membership_start
        except sender.DoesNotExist:
            instance._old_membership_plan_id = None
            instance._old_membership_start = None
    else:
        instance._old_membership_plan_id = None
        instance._old_membership_start = None


@receiver(post_save, sender=Member)
def create_member_snapshot(sender, instance, created, **kwargs):
    if created:
        PaymentHistory.objects.create(
            member=instance,
            membership_plan=instance.membership_plan,
            plan_name_snapshot=instance.membership_plan.name if instance.membership_plan else "N/A",
            plan_price_snapshot=instance.membership_plan.price if instance.membership_plan else 0,
            plan_duration_snapshot=instance.membership_plan.duration_days if instance.membership_plan else 0,
            membership_start=instance.membership_start,
            membership_end=instance.membership_end,
            transaction_type='initial',
            payment_amount=instance.amount_paid,
            renewal_count=instance.renewal_count,
        )
    else:
        old_plan_id = getattr(instance, '_old_membership_plan_id', None)
        old_start = getattr(instance, '_old_membership_start', None)
        new_plan_id = instance.membership_plan_id
        new_start = instance.membership_start

        # Plan changed
        if old_plan_id != new_plan_id:
            PaymentHistory.objects.create(
                member=instance,
                membership_plan=instance.membership_plan,
                plan_name_snapshot=instance.membership_plan.name if instance.membership_plan else "N/A",
                plan_price_snapshot=instance.membership_plan.price if instance.membership_plan else 0,
                plan_duration_snapshot=instance.membership_plan.duration_days if instance.membership_plan else 0,
                membership_start=new_start,
                membership_end=instance.membership_end,
                transaction_type='plan_change',
                payment_amount=instance.amount_paid,
                renewal_count=instance.renewal_count,
            )

        # Start date changed
        if old_start != new_start:
            PaymentHistory.objects.create(
                member=instance,
                membership_plan=instance.membership_plan,
                plan_name_snapshot=instance.membership_plan.name if instance.membership_plan else "N/A",
                plan_price_snapshot=instance.membership_plan.price if instance.membership_plan else 0,
                plan_duration_snapshot=instance.membership_plan.duration_days if instance.membership_plan else 0,
                membership_start=new_start,
                membership_end=instance.membership_end,
                transaction_type='renewal',
                payment_amount=instance.amount_paid,
                renewal_count=instance.renewal_count,
            )