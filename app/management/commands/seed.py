from django.core.management.base import BaseCommand
from django.utils import timezone
from app.models import MstUser, MstOrg, MstClient, MstLocation, MapLocGuard, TransDuty, TransAlert, LogLoc
import random
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **kwargs):
        # Seed MstOrg
        orgs = []
        for i in range(10):
            org, created = MstOrg.objects.get_or_create(
                org_name=f'Organization{i}',
                defaults={'logo': f'Logo{i}', 'address': f'Address{i}'}
            )
            if not created:
                self.stdout.write(f'Skipped existing MstOrg: {org.org_name}')
            else:
                orgs.append(org)

        # Seed MstUser
        users = []
        orgs = list(MstOrg.objects.all())
        for i in range(10):
            username = f'User{i}'
            try:
                user, created = MstUser.objects.get_or_create(
                    username=username,
                    defaults={
                        'role_id': i,  # Adjust as needed
                        'user_mob': f'123456789{i:02d}',
                        'pin': make_password('1234'),  # Hashing the pin
                        'otp': '5678',
                        'org_id': random.choice(orgs).org_id,
                        'fcm': f'fcm_token_{i}'
                    }
                )
                if created:
                    users.append(user)
                else:
                    self.stdout.write(f'Skipped existing MstUser: {username}')
            except IntegrityError:
                self.stdout.write(f'Skipped due to IntegrityError: {username}')

        # Seed MstClient
        for i in range(10):
            client, created = MstClient.objects.get_or_create(
                cl_name=f'Client{i}',
                defaults={
                    'contact_per': f'ContactPerson{i}',
                    'contact_mob1': f'123456789{i}',
                    'contact_mob2': f'987654321{i}',
                    'org_id': random.choice(orgs)
                }
            )
            if not created:
                self.stdout.write(f'Skipped existing MstClient: {client.cl_name}')

        # Seed MstLocation
        orgs = list(MstOrg.objects.all())
        # Predefined set of latitude and longitude pairs
        coordinates = [
            ('12.9716', '77.5946'),  # Bangalore
            ('28.7041', '77.1025'),  # Delhi
            ('19.0760', '72.8777'),  # Mumbai
            ('13.0827', '80.2707'),  # Chennai
            ('22.5726', '88.3639'),  # Kolkata
            ('23.0225', '72.5714'),  # Ahmedabad
            ('18.5204', '73.8567'),  # Pune
            ('26.8467', '80.9462'),  # Lucknow
            ('25.3176', '82.9739'),  # Varanasi
            ('17.3850', '78.4867')   # Hyderabad
        ]

        for i, coord in enumerate(coordinates):
            lati, longi = coord
            location, created = MstLocation.objects.get_or_create(
                loc_name=f'Location{i}',
                defaults={
                    'lati': lati,
                    'longi': longi,
                    'sec_hours': '8',
                    'contact_per': f'LocationContact{i}',
                    'contact_mob1': f'123456789{i}',
                    'contact_mob2': f'987654321{i}',
                    'org_id': random.choice(orgs) if orgs else None
                }
            )
            if not created:
                self.stdout.write(f'Skipped existing MstLocation: {location.loc_name}')
            else:
                print(f"Created MstLocation: {location.loc_name}")

        # Seed MapLocGuard
        orgs = list(MstOrg.objects.all())
        for i in range(10):
            MapLocGuard.objects.create(
                loc_id=MstLocation.objects.get(pk=i+1),
                user_id=random.choice(users),
                org_id=random.choice(orgs),
                cl_id=MstClient.objects.get(pk=i+1)
            )

        # Seed TransDuty
        for i in range(10):
            TransDuty.objects.create(
                user_id=random.choice(users),
                loc_id=MstLocation.objects.get(pk=i+1),
                duty_dt=timezone.now().date(),
                st_time=timezone.now(),
                end_time=timezone.now()
            )

        # Seed TransAlert
        for i in range(10):
            try:
                user = random.choice(users)
                supervisor = random.choice(users)
                reason = random.choice([TransAlert.OUT_OF_LOCATION, TransAlert.MISSED_TO_PUNCH])
                org = random.choice(orgs)
                st_time = timezone.now()
                end_time = timezone.now() + timezone.timedelta(hours=1)  # Adjust as needed

                # Check if an alert with these exact parameters already exists
                alert_exists = TransAlert.objects.filter(
                    user_id=user, 
                    sup_id=supervisor, 
                    reason=reason, 
                    st_time=st_time, 
                    end_time=end_time, 
                    org_id=org
                ).exists()

                if not alert_exists:
                    alert = TransAlert.objects.create(
                        user_id=user,
                        sup_id=supervisor,
                        reason=reason,
                        st_time=st_time,
                        end_time=end_time,
                        org_id=org
                    )
                else:
                    print("Skipped existing TransAlert")
            except Exception as e:
                print(f"Error creating TransAlert: {e}")

        # Seed LogLoc
        for i in range(10):
            log, created = LogLoc.objects.get_or_create(
                user_id=random.choice(users),
                tm=timezone.now(),
                defaults={
                    'lati': '12.345678',
                    'longi': '98.765432'
                }
            )
            if not created:
                self.stdout.write(f'Skipped existing LogLoc')

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database'))