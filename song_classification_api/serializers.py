from rest_framework import serializers
from .models import Song, SongFingerprint

class SongSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Song
        fields = ('name', 'artist')
    
# class SongSerializer(serializers.HyperlinkedModelSerializer):
#     class meta:
#         model = SongFingerprint
#         field = ('hash')