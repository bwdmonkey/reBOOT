from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from datetime import datetime


class ResourceManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(ResourceManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return ResourceQuerySet(self.model).alive()
        return ResourceQuerySet(self.model)

    def destroy(self):
        return self.get_queryset().hard_delete()


class ResourceModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    created_at_formatted = models.CharField(max_length=10, blank=True, verbose_name="Date Created in Y-M-D")

    objects = ResourceManager()
    all_objects = ResourceManager(alive_only=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.created_at_formatted:
            self.created_at_formatted = datetime.utcnow().strftime("%Y-%m-%d")
        super(ResourceModel, self).save(*args, **kwargs)        

    def delete(self):
        self.deleted_at = datetime.utcnow()
        self.save()

    def destroy(self):
        super(ResourceModel, self).delete()


class ResourceQuerySet(QuerySet):
    def delete(self):
        return super(ResourceQuerySet, self).update(deleted_at=datetime.utcnow())

    def destroy(self):
        return super(ResourceQuerySet, self).delete()

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)