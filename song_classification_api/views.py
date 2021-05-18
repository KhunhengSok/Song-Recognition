from django.shortcuts import render
from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import FileSystemStorage

from .serializers import SongSerializer
from .models import Song
import os
from datetime import datetime
from Song_Classification.settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR

# Create your views here.
# class SongViewSet(viewsets.ModelViewSet):
class SongViewSet(viewsets.ModelViewSet):
    querySet = Song.objects.all()
    serializer_class = SongSerializer

    def retrieve(self, request, pk=None):
        song = None 
        try: 
            song = Song.objects.get(id=pk)
        except Song.DoesNotExist:
            pass

        if not song:
            return Response(status=status.HTTP_404_NOT_FOUND, data = {'msg': 'Not Found'})
        else: 
            serializer = SongSerializer(song)
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        print(request.FILES)
        file = request.FILES['recorded']
        date  = datetime.today().strftime('%Y-%m-%d')
        date = os.path.join(MEDIA_ROOT, date)
        os.makedirs(date, exist_ok=True)
 
        fs = FileSystemStorage(date)
        filename = fs.save(file.name, file)
        uploaded_file_url = fs.url(filename)
        file_full_path = os.path.join(MEDIA_ROOT, uploaded_file_url)
        
        return Response(file_full_path)

    

class SongView(views.APIView):
    querySet = Song.objects.all()
    serializer_class = SongSerializer

    def get(self, request, key=None):
        print(request)
        return Response('Hello world')