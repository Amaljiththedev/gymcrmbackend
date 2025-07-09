
from decimal import Decimal
from celery import shared_task
from datetime import datetime
from django.utils.timezone import make_aware
from interfaces.members.models import Member, MembershipPlan

@shared_task
def renew_membership_task(member_id, payment_amount, new_plan_id, new_start_date):
    from interfaces.members.models import Member, MembershipPlan
    from django.utils.timezone import make_aware
    from datetime import datetime
    import logging

    try:
        member = Member.objects.get(id=member_id)
        new_plan = MembershipPlan.objects.get(id=new_plan_id)

        # Parse ISO datetime string safely
        new_start = make_aware(datetime.fromisoformat(new_start_date))

        # 🔥 Convert payment_amount to Decimal
        member.membership_plan = new_plan
        member.membership_start = new_start
        member.amount_paid = Decimal(str(payment_amount))  # ✅ Safe conversion
        member.renewal_count += 1
        member.save()  # Triggers signals

    except Exception as e:
        logging.error(f"[Renewal Task Error] Member ID {member_id}: {e}")