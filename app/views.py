from datetime import datetime
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import MstUser
from django.contrib.auth.hashers import make_password
from .models import MstLocation
from .serializers import MstLocationSerializer
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance

class LoginAPIView(APIView):
    def post(self, request):
        user_mob = request.data.get('user_mob')
        pin = request.data.get('pin')
        user = authenticate(user_mob=user_mob, pin=pin)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
    
class SignupAPIView(APIView):
    def post(self, request):
        # Extracting required fields from request.data
        username = request.data.get('username')
        user_mob = request.data.get('user_mob')
        pin = request.data.get('pin')
        role_id = request.data.get('role_id')
        org_id = request.data.get('org_id', None)  # Optional, with default value
        fcm = request.data.get('fcm', None)  # Optional, with default value
        sup_id = request.data.get('sup_id', None)  # Optional, with default value
        date_joined = datetime.now()

        # Validate required fields
        if not all([username, user_mob, pin, role_id]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Creating a new user
            user = MstUser.objects.create(
                username=username,
                user_mob=user_mob,
                pin=make_password(pin),
                role_id=role_id,
                org_id=org_id,
                fcm=fcm,
                sup_id=sup_id,
                date_joined=date_joined
            )

            # Create JWT token
            refresh = RefreshToken.for_user(user)

            # Return token and user data
            return Response({
                'username': user.username,
                'user_mob': user.user_mob,
                'token': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class LocationSuggestionView(APIView):
    def get(self, request):
        # Extract lati and longi from request query parameters
        try:
            user_lati = float(request.query_params.get('lati'))
            user_longi = float(request.query_params.get('longi'))
            print("lati:", user_lati, ",","longi:", user_longi )
        except (TypeError, ValueError):
            return Response({'error': 'Invalid latitude or longitude'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Create a Point object for the user's location
        user_location = Point(user_longi, user_lati, srid=4326)

        # Query the nearest locations
        nearest_locations = MstLocation.objects.annotate(
            distance=Distance('location', user_location)
        ).order_by('distance')[:10] # Change 10 to your desired number of suggestions
        for loc in nearest_locations:
            print(loc.distance.km, loc.loc_name, "d")

        # Serialize the queryset
        serializer = MstLocationSerializer(nearest_locations, many=True)
        return Response(serializer.data)