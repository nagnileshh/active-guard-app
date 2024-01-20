# Generated by Django 5.0.1 on 2024-01-20 21:04

import django.contrib.gis.db.models.fields
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MstOrg',
            fields=[
                ('org_id', models.AutoField(primary_key=True, serialize=False)),
                ('org_name', models.CharField(max_length=100, unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]*$', 'Only alphanumeric characters and @/./+/-/_ are allowed.')])),
                ('logo', models.CharField(max_length=300)),
                ('address', models.CharField(blank=True, max_length=300)),
            ],
            options={
                'verbose_name': 'Organization',
                'verbose_name_plural': 'Organizations',
            },
        ),
        migrations.CreateModel(
            name='MstUser',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('role_id', models.IntegerField()),
                ('username', models.CharField(max_length=50, unique=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')])),
                ('user_mob', models.CharField(max_length=15, unique=True, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.')])),
                ('pin', models.CharField(max_length=128, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.')])),
                ('otp', models.CharField(blank=True, max_length=4, null=True, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.')])),
                ('org_id', models.IntegerField(blank=True, null=True)),
                ('fcm', models.CharField(blank=True, max_length=255, null=True)),
                ('sup_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
        ),
        migrations.CreateModel(
            name='MstLocation',
            fields=[
                ('loc_id', models.AutoField(primary_key=True, serialize=False)),
                ('loc_name', models.CharField(max_length=100, validators=[django.core.validators.RegexValidator('^[\\w.@+-]*$', 'Only alphanumeric characters and @/./+/-/_ are allowed.'), django.core.validators.MinLengthValidator(3)])),
                ('lati', models.CharField(max_length=15)),
                ('longi', models.CharField(max_length=15)),
                ('location', django.contrib.gis.db.models.fields.PointField(geography=True, null=True, srid=4326)),
                ('sec_hours', models.CharField(max_length=50)),
                ('contact_per', models.CharField(blank=True, max_length=50, validators=[django.core.validators.RegexValidator('^[\\w.@+-]*$', 'Only alphanumeric characters and @/./+/-/_ are allowed.'), django.core.validators.MinLengthValidator(3)])),
                ('contact_mob1', models.CharField(blank=True, max_length=15, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.'), django.core.validators.MinLengthValidator(9)])),
                ('contact_mob2', models.CharField(blank=True, max_length=15, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.'), django.core.validators.MinLengthValidator(9)])),
                ('org_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.mstorg')),
            ],
            options={
                'verbose_name': 'Location',
                'verbose_name_plural': 'Locations',
            },
        ),
        migrations.CreateModel(
            name='MstClient',
            fields=[
                ('cl_id', models.AutoField(primary_key=True, serialize=False)),
                ('cl_name', models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.RegexValidator('^[\\w.@+-]*$', 'Only alphanumeric characters and @/./+/-/_ are allowed.')])),
                ('contact_per', models.CharField(blank=True, max_length=50, validators=[django.core.validators.MinLengthValidator(3)])),
                ('contact_mob1', models.CharField(blank=True, max_length=15, validators=[django.core.validators.MinLengthValidator(9), django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.')])),
                ('contact_mob2', models.CharField(blank=True, max_length=15, validators=[django.core.validators.MinLengthValidator(9), django.core.validators.RegexValidator('^[0-9]*$', 'Only numeric characters are allowed.')])),
                ('org_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clients', to='app.mstorg')),
            ],
            options={
                'verbose_name': 'Client',
                'verbose_name_plural': 'Clients',
            },
        ),
        migrations.CreateModel(
            name='MapLocGuard',
            fields=[
                ('loc_gd_id', models.AutoField(primary_key=True, serialize=False)),
                ('cl_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.mstclient')),
                ('loc_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.mstlocation')),
                ('org_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.mstorg')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.mstuser')),
            ],
            options={
                'verbose_name': 'Location Guard Mapping',
                'verbose_name_plural': 'Location Guard Mappings',
            },
        ),
        migrations.CreateModel(
            name='LogLoc',
            fields=[
                ('loc_id', models.AutoField(primary_key=True, serialize=False)),
                ('lati', models.CharField(max_length=15)),
                ('longi', models.CharField(max_length=15)),
                ('tm', models.DateTimeField(default=django.utils.timezone.now)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.mstuser')),
            ],
            options={
                'verbose_name': 'Location Log',
                'verbose_name_plural': 'Location Logs',
            },
        ),
        migrations.CreateModel(
            name='TransAlert',
            fields=[
                ('alert_id', models.AutoField(primary_key=True, serialize=False)),
                ('reason', models.IntegerField(choices=[(1, 'Out of Location'), (2, 'Missed to Punch')])),
                ('st_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('org_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.mstorg')),
                ('sup_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supervisor_alerts', to='app.mstuser')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_alerts', to='app.mstuser')),
            ],
            options={
                'verbose_name': 'Alert',
                'verbose_name_plural': 'Alerts',
            },
        ),
        migrations.CreateModel(
            name='TransDuty',
            fields=[
                ('duty_id', models.AutoField(primary_key=True, serialize=False)),
                ('duty_dt', models.DateField()),
                ('st_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('loc_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.mstlocation')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.mstuser')),
            ],
            options={
                'verbose_name': 'Duty Transaction',
                'verbose_name_plural': 'Duty Transactions',
            },
        ),
        migrations.AddConstraint(
            model_name='mstlocation',
            constraint=models.UniqueConstraint(fields=('loc_name', 'org_id'), name='unique_location_per_org'),
        ),
        migrations.AddConstraint(
            model_name='mstclient',
            constraint=models.UniqueConstraint(fields=('cl_name', 'org_id'), name='unique_client_per_org'),
        ),
    ]