from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from grd import views


router = routers.DefaultRouter()
router.register(r'devices', views.DeviceView)

urlpatterns = [
    # Examples:
    # url(r'^$', 'ereuse.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^api-token-auth/', obtain_auth_token),
    
    url(r'^api/register/$', views.Register.as_view(), name='do-register'),
    url(r'^api/devices/(?P<pk>[^/.]+)/log/$',
        views.DeviceLog.as_view({'get': 'list'}), name='device-log'),
    url(r'^api/devices/(?P<pk>[^/.]+)/recycle/$', views.Recycle.as_view(),
        name='do-recycle'),
]
