from rest_framework import serializers
from .models import MstUser
from django.contrib.auth.hashers import make_password
from .models import MstLocation

class MstUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MstUser
        fields = ['user_id', 'role_id', 'username', 'user_mob', 'pin', 'otp', 'org_id', 'fcm', 'sup_id']
        extra_kwargs = {
            'user_id': {'read_only': True},
            'otp': {'write_only': True},
            'pin': {'write_only': True},
            'sup_id': {'required': False},
            'org_id': {'required': False},
            'fcm': {'required': False}
        }

    def create(self, validated_data):
        validated_data['pin'] = make_password(validated_data['pin'])
        return MstUser.objects.create(**validated_data)

class MstLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MstLocation
        fields = ['loc_id', 'loc_name', 'lati', 'longi', 'sec_hours', 'contact_per', 'contact_mob1', 'contact_mob2', 'org_id']