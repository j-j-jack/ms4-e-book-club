from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import OrderLineItemProduct, OrderLineItemSubscription


@receiver(post_save, sender=OrderLineItemProduct)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    instance.order.update_total()


@receiver(post_delete, sender=OrderLineItemProduct)
def update_on_delete(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    instance.order.update_total()


@receiver(post_save, sender=OrderLineItemSubscription)
def update_on_save_subscription(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    instance.order.update_subscription_total()


@receiver(post_delete, sender=OrderLineItemSubscription)
def update_on_delete_subscription(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    instance.order.update_subscription_total()
