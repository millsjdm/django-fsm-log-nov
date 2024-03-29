# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.timezone import now
from django_fsm import FSMFieldMixin, FSMIntegerField

from .conf import settings
from .managers import StateLogManager


@python_2_unicode_compatible
class StateLog(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    timestamp = models.DateTimeField(
        default=now,
    )
    by = models.ForeignKey(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    state = models.CharField(
        max_length=255,
        db_index=True,
    )
    transition = models.CharField(
        max_length=255,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.UUIDField(
        db_index=True,
    )
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )
    description = models.TextField(
        blank=True,
    )

    objects = StateLogManager()

    class Meta:
        get_latest_by = 'timestamp'

    class JSONAPIMeta:
        resource_name = "statelog"

    def __str__(self):
        return '{} - {} - {}'.format(
            self.timestamp,
            self.content_object,
            self.transition,
        )

    def get_state_display(self):
        fsm_cls = self.content_type.model_class()
        for field in fsm_cls._meta.fields:
            if isinstance(field, FSMIntegerField):
                state_display = dict(field.flatchoices).get(int(self.state), self.state)
                return force_text(state_display, strings_only=True)
            elif isinstance(field, FSMFieldMixin):
                state_display = dict(field.flatchoices).get(self.state, self.state)
                return force_text(state_display, strings_only=True)
