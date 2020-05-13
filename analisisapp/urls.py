from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from tweetapp import views
from django.conf.urls import url

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'tweet', views.TweetViewSet)
# router.register(r'getLabel', views.TweetViewSet.get)

urlpatterns = [
    url(r'^getLabel/', views.getLabel),
    url(r'^train/', views.Train.as_view(), name="train"),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
]
