from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from grd import views


router = routers.DefaultRouter()
router.register(r'devices', views.DeviceView)
router.register(r'events', views.EventView)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^api-token-auth/', obtain_auth_token),
]
