from datetime import timedelta
from django.core.cache import cache
from django.utils import timezone
from .models import Member
from django.db.models import F


def get_active_members():
    cache_key = 'active_members'
    result = cache.get(cache_key)
    if result is None:
        now = timezone.now()
        qs = Member.objects.filter(membership_end__gte=now, is_blocked=False)
        result = list(qs.values())
        cache.set(cache_key, result, timeout=None)  # Indefinite caching
    return result

def get_expired_members():
    cache_key = 'expired_members'
    result = cache.get(cache_key)
    if result is None:
        now = timezone.now()
        qs = Member.objects.filter(membership_end__lt=now)
        result = list(qs.values())
        cache.set(cache_key, result, timeout=None)
    return result

def get_expiring_members():
    cache_key = 'expiring_members'
    result = cache.get(cache_key)
    if result is None:
        today = timezone.now().date()
        upcoming_expiry_date = today + timedelta(days=5)
        qs = Member.objects.filter(
            is_blocked=False,
            membership_end__gte=today,
            membership_end__lte=upcoming_expiry_date
        )
        result = list(qs.values())
        cache.set(cache_key, result, timeout=None)
    return result


def get_not_fully_paid_members():
    cache_key = 'not_fully_paid_members'
    result = cache.get(cache_key)
    if result is None:
        qs = Member.objects.filter(amount_paid__lt=F('membership_plan__price')).exclude(amount_paid__isnull=True)
        result = list(qs.values())  # Returns all fields as a dict for each member.

        cache.set(cache_key, result, timeout=None)  # Cached indefinitely until invalidated
    return result