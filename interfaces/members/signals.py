
from functools import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from interfaces.members.models import Member

def invalidate_members_cache():
    cache.delete('active_members')
    cache.delete('expired_members')
    cache.delete('expiring_members')
    cache.delete('not_fully_paid_members')

@receiver(post_save, sender=Member)
def member_post_save(sender, instance, **kwargs):
    invalidate_members_cache()

@receiver(post_delete, sender=Member)
def member_post_delete(sender, instance, **kwargs):
    invalidate_members_cache()
