from django.db import models
from django.utils import timezone

# Create your models here.

# start TimeStamp #
class TimeStamp(models.Model):
    """Base class containing all models common information."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted=models.BooleanField(default=False)
    deleted_at=models.DateTimeField(blank=True, null=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        """Define Model as abstract."""
        abstract = True
# end TimeStamp #

# start Client #
class Client(TimeStamp):
    name = models.CharField(max_length=255)
    mobile = models.PositiveIntegerField(null=True)

    def save(self, **kwargs):
        super(Client, self).save()
    
    class Meta:
        db_table = 'client'
# end Client #