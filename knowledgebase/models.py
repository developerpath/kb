from django.db import models
from knowledgebase.valid import *
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

User._meta.get_field('email')._unique = True

class UserExtended(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    user_avatar = models.TextField(blank=True)
    user_desc = models.TextField(blank=True)
    user_phone = models.CharField(max_length=25, blank=True)
    user_address = models.CharField(max_length=250, blank=True)
    user_city = models.CharField(max_length=250, blank=True)
    user_prov = models.CharField(max_length=250, blank=True)
    user_postal = models.CharField(max_length=250, blank=True)
    user_country = models.CharField(max_length=250, blank=True)
    
    @receiver(post_save, sender=User)
    def create_or_update_user(sender, instance, created, **kwargs):
        if created:
            instance.userextended = UserExtended.objects.create(user=instance)
        instance.userextended.save()

    def __str__(self):
        return self.user.username

class Page(models.Model):
    page_title = models.CharField(max_length=250)
    page_type = models.CharField(max_length=250, blank=True)
    page_version = models.PositiveIntegerField(default=1)
    page_content = models.TextField()
    page_parent_id = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null = True,
        blank = True,
    )
    draft_parent_id = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null = True,
        blank = True,
        related_name='+',
    )
    space_id = models.ForeignKey(
        'Space',
        on_delete=models.SET_NULL,
        null = True,
        blank = True
    )
    page_creator = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='+',
        to_field='username',
        default='admin',
        null=False,
    )
    page_modifier = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='+',
        to_field='username',
        default='admin',
        null=False,
    )
    page_created = models.DateTimeField(auto_now_add=True, null=False)
    page_updated = models.DateTimeField(auto_now=True, null=False)
    
    def clean(self):
        if self.pk and self.pk == self.page_parent_id_id:
            raise ValidationError({
                'page_parent_id': ValidationError(_(
                    """The page can not be sub-item of itself.
                    Please select different page."""))
            })

    def __str__(self):
        return self.page_title

class Space(models.Model):
    space_id = models.AutoField(primary_key=True)
    space_title = models.CharField(max_length=250)
    space_description = models.TextField(blank=True)
    space_home_id = models.OneToOneField(
        Page,
        on_delete=models.PROTECT,
    )
    space_created = models.DateTimeField(auto_now_add=True, null=False)
    space_updated = models.DateTimeField(auto_now=True, null=False)
    
    def __str__(self):
        return self.space_title
    
class Activity(models.Model):
    activity_id = models.AutoField(primary_key=True)
    activity_relation = models.CharField(max_length=250, null=False)
    activity_type = models.CharField(max_length=250, null=False)
    activity_page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='+',
        to_field='id',
        null = True,
    )
    activity_space = models.ForeignKey(
        Space,
        on_delete=models.CASCADE,
        related_name='+',
        to_field='space_id',
        null = True,
    )
    activity_creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='+',
        to_field='username',
        null=False,
    )
    activity_created = models.DateTimeField(auto_now_add=True, null=False)
