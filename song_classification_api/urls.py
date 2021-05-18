from django.urls import path, include
from .views import SongView, SongViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'', SongViewSet, basename='Song')

urlpatterns = [
    # path('search', views.SongViewSet, name='search' ),
    # path('search/', SongView, name='search' ),
    path('songs/', include(router.urls), name='search' ),
]





