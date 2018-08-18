from django.db import models
from django.db.models import fields


class Node(models.Model):
    title = fields.TextField()
    parent = models.ForeignKey('Node', default=None, related_name='descendants', on_delete=models.SET_NULL, null=True, blank=True)
