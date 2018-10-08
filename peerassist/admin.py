from django.contrib import admin
from django_peeringdb.models import *

admin.site.register(Organization)
admin.site.register(Facility)
admin.site.register(Network)
admin.site.register(InternetExchange)
admin.site.register(InternetExchangeFacility)
admin.site.register(IXLan)
admin.site.register(IXLanPrefix)
admin.site.register(NetworkContact)
admin.site.register(NetworkFacility)
admin.site.register(NetworkIXLan)
