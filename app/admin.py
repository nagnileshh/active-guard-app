from django.contrib import admin
from .models import MstUser, MstOrg, MstClient, MstLocation, MapLocGuard, TransDuty, TransAlert, LogLoc

admin.site.register(MstUser)
admin.site.register(MstOrg)
admin.site.register(MstClient)
admin.site.register(MstLocation)
admin.site.register(MapLocGuard)
admin.site.register(TransDuty)
admin.site.register(TransAlert)
admin.site.register(LogLoc)
