from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
import uuid

class MstOrg(models.Model):
    alphanumeric_special = RegexValidator(r'^[\w.@+-]*$', 'Only alphanumeric characters and @/./+/-/_ are allowed.')
    
    org_id = models.AutoField(primary_key=True)
    org_name = models.CharField(max_length=100, unique=True, validators=[alphanumeric_special])
    logo = models.CharField(max_length=300)
    address = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.org_name

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'

class MstUser(models.Model):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
    numeric = RegexValidator(r'^[0-9]*$', 'Only numeric characters are allowed.')

    # Assuming user_id is auto-incremented and is the primary key
    user_id = models.AutoField(primary_key=True)
    role_id = models.IntegerField()  # ForeignKey if there's a Role model for system roles
    username = models.CharField(max_length=50, validators=[alphanumeric], unique=True)
    user_mob = models.CharField(max_length=15, unique=True, validators=[numeric])
    pin = models.CharField(max_length=128, validators=[numeric])
    otp = models.CharField(max_length=4, validators=[numeric], null=True, blank=True)
    org_id = models.IntegerField(null=True, blank=True)  # ForeignKey if there's an Org model for organization IDs
    fcm = models.CharField(max_length=255, null=True, blank=True)  # Assuming FCM is a string
    sup_id = models.IntegerField(null=True, blank=True)  # ForeignKey if it references another user
    date_joined = models.DateTimeField(auto_now_add=True)

    # Add __str__ method to return a string representation of the user
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class MstClient(models.Model):
    alphanumeric_special = RegexValidator(r'^[\w.@+-]*$', 'Only alphanumeric characters and @/./+/-/_ are allowed.')
    numeric = RegexValidator(r'^[0-9]*$', 'Only numeric characters are allowed.')

    cl_id = models.AutoField(primary_key=True)
    cl_name = models.CharField(max_length=100, validators=[MinLengthValidator(3), alphanumeric_special])
    contact_per = models.CharField(max_length=50, blank=True, validators=[MinLengthValidator(3)])
    contact_mob1 = models.CharField(max_length=15, blank=True, validators=[MinLengthValidator(9), numeric])
    contact_mob2 = models.CharField(max_length=15, blank=True, validators=[MinLengthValidator(9), numeric])
    org_id = models.ForeignKey(
        'MstOrg',
        on_delete=models.CASCADE,
        related_name='clients'
    )

    def __str__(self):
        return self.cl_name

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        constraints = [
            models.UniqueConstraint(fields=['cl_name', 'org_id'], name='unique_client_per_org')
        ]

class MstLocation(models.Model):
    alphanumeric_special = RegexValidator(
        r'^[\w.@+-]*$', 'Only alphanumeric characters and @/./+/-/_ are allowed.')
    numeric = RegexValidator(r'^[0-9]*$', 'Only numeric characters are allowed.')

    loc_id = models.AutoField(primary_key=True)
    loc_name = models.CharField(max_length=100, validators=[
                                alphanumeric_special, MinLengthValidator(3)])
    lati = models.CharField(max_length=15)  # Assuming latitude is stored as a string
    longi = models.CharField(max_length=15)  # Assuming longitude is stored as a string
    location = gis_models.PointField(geography=True, null=True)
    # sec_hours field type needs to be decided; for now, it's a CharField.
    sec_hours = models.CharField(max_length=50)  # Placeholder, adjust the max_length as needed
    contact_per = models.CharField(
        max_length=50, validators=[alphanumeric_special, MinLengthValidator(3)], blank=True)
    contact_mob1 = models.CharField(
        max_length=15, validators=[numeric, MinLengthValidator(9)], blank=True)
    contact_mob2 = models.CharField(
        max_length=15, validators=[numeric, MinLengthValidator(9)], blank=True)
    # org_id is a ForeignKey to the MstOrg model
    org_id = models.ForeignKey('MstOrg', on_delete=models.CASCADE)

    def __str__(self):
        return self.loc_name

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        constraints = [
            models.UniqueConstraint(fields=['loc_name', 'org_id'], name='unique_location_per_org')
        ]

    def save(self, *args, **kwargs):
        # Create Point from lati and longi
        if self.lati and self.longi:
            self.location = Point(float(self.longi), float(self.lati))

        super(MstLocation, self).save(*args, **kwargs)

class MapLocGuard(models.Model):
    loc_gd_id = models.AutoField(primary_key=True)
    loc_id = models.ForeignKey('MstLocation', on_delete=models.CASCADE)
    user_id = models.ForeignKey('MstUser', on_delete=models.CASCADE)
    org_id = models.ForeignKey('MstOrg', on_delete=models.CASCADE)
    cl_id = models.ForeignKey('MstClient', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Mapping {self.loc_gd_id}: Location {self.loc_id} - Guard {self.user_id}"

    class Meta:
        verbose_name = 'Location Guard Mapping'
        verbose_name_plural = 'Location Guard Mappings'

class TransDuty(models.Model):
    duty_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('MstUser', on_delete=models.CASCADE)
    loc_id = models.ForeignKey('MstLocation', on_delete=models.CASCADE)
    duty_dt = models.DateField()
    st_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"Duty {self.duty_id} - User {self.user_id} at Location {self.loc_id}"

    def save(self, *args, **kwargs):
        if self.pk and self.end_time:  # Check if it's an existing record and end_time is set
            original = TransDuty.objects.get(pk=self.pk)
            if original.end_time != self.end_time:
                raise ValidationError("End time cannot be changed once it's set.")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Duty Transaction'
        verbose_name_plural = 'Duty Transactions'

class TransAlert(models.Model):
    # Enum for reasons
    OUT_OF_LOCATION = 1
    MISSED_TO_PUNCH = 2
    REASON_CHOICES = [
        (OUT_OF_LOCATION, 'Out of Location'),
        (MISSED_TO_PUNCH, 'Missed to Punch'),
    ]

    alert_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('MstUser', on_delete=models.CASCADE, related_name='user_alerts')
    sup_id = models.ForeignKey('MstUser', on_delete=models.CASCADE, related_name='supervisor_alerts')
    reason = models.IntegerField(choices=REASON_CHOICES)
    st_time = models.DateTimeField(null=True, blank=True)  # Nullable as it depends on the reason
    end_time = models.DateTimeField(null=True, blank=True)  # Nullable as it depends on the reason
    org_id = models.ForeignKey('MstOrg', on_delete=models.CASCADE)

    def __str__(self):
        return f"Alert {self.alert_id} - User {self.user_id}"

    def save(self, *args, **kwargs):
        # Uncommented and corrected validation logic
        if self.reason == self.OUT_OF_LOCATION and not (self.st_time and self.end_time):
            raise ValidationError('Start time and end time are mandatory for Out of Location alerts.')

        # Check if end_time is being modified on an existing record
        if self.pk:
            original = TransAlert.objects.get(pk=self.pk)
            if original.end_time and original.end_time != self.end_time:
                raise ValidationError("End time cannot be changed once it's set.")

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'

class LogLoc(models.Model):
    loc_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('MstUser', on_delete=models.CASCADE)
    lati = models.CharField(max_length=15)
    longi = models.CharField(max_length=15)
    tm = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Location Log {self.loc_id} for User {self.user_id}"

    class Meta:
        verbose_name = 'Location Log'
        verbose_name_plural = 'Location Logs'

class Token(models.Model):
    user = models.ForeignKey('MstUser', on_delete=models.CASCADE)
    token = models.CharField(max_length=255, default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.user_mob}"