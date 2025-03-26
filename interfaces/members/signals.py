from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from .models import Member, PaymentHistory

# Temporary storage for old state of Member instances
OLD_MEMBER_STATE = {}

@receiver(pre_save, sender=Member)
def capture_old_member_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            OLD_MEMBER_STATE[instance.pk] = {
                'membership_plan_id': old_instance.membership_plan_id,
                'amount_paid': old_instance.amount_paid,
                'membership_start': old_instance.membership_start,
                'membership_end': old_instance.membership_end,
                'renewal_count': old_instance.renewal_count,
            }
        except sender.DoesNotExist:
            pass

@receiver(post_save, sender=Member)
def create_member_snapshot(sender, instance, created, **kwargs):
    # Invalidate cache for this member's PaymentHistory if using Redis caching.
    cache_key = f'payment_history_{instance.pk}'
    cache.delete(cache_key)

    if created:
        # Create initial snapshot.
        PaymentHistory.objects.create(
            member=instance,
            membership_plan=instance.membership_plan,
            plan_name_snapshot=(instance.membership_plan.name if instance.membership_plan else ''),
            plan_price_snapshot=(instance.membership_plan.price if instance.membership_plan else 0),
            plan_duration_snapshot=(instance.membership_plan.duration_days if instance.membership_plan else 0),
            membership_start=instance.membership_start,
            membership_end=instance.membership_end,
            transaction_type='initial',
            payment_amount=instance.amount_paid,
            renewal_count=instance.renewal_count,
        )
    else:
        old_state = OLD_MEMBER_STATE.pop(instance.pk, None)
        if not old_state:
            return

        membership_plan_changed = (old_state['membership_plan_id'] != instance.membership_plan_id)
        amount_paid_changed = (old_state['amount_paid'] != instance.amount_paid)

        if membership_plan_changed:
            # For a plan change (renewal), increment renewal_count.
            instance.renewal_count = old_state['renewal_count'] + 1
            PaymentHistory.objects.create(
                member=instance,
                membership_plan=instance.membership_plan,
                plan_name_snapshot=(instance.membership_plan.name if instance.membership_plan else ''),
                plan_price_snapshot=(instance.membership_plan.price if instance.membership_plan else 0),
                plan_duration_snapshot=(instance.membership_plan.duration_days if instance.membership_plan else 0),
                membership_start=instance.membership_start,
                membership_end=instance.membership_end,
                transaction_type='renewal',
                payment_amount=instance.amount_paid,  # For renewal, amount_paid is the new cycle's payment.
                renewal_count=instance.renewal_count,
            )
        elif amount_paid_changed:
            diff_payment = instance.amount_paid - old_state['amount_paid']
            PaymentHistory.objects.create(
                member=instance,
                membership_plan=instance.membership_plan,
                plan_name_snapshot=(instance.membership_plan.name if instance.membership_plan else ''),
                plan_price_snapshot=(instance.membership_plan.price if instance.membership_plan else 0),
                plan_duration_snapshot=(instance.membership_plan.duration_days if instance.membership_plan else 0),
                membership_start=instance.membership_start,
                membership_end=instance.membership_end,
                transaction_type='payment',
                payment_amount=diff_payment,
                renewal_count=instance.renewal_count,
            )
