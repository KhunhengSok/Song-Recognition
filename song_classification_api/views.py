from song_classification_api.Core import DatabaseHandler
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

from .Core.util  import * 
from . import Core
from song_classification_api.Core import util 

# Create your views here.
# class SongViewSet(viewsets.ModelViewSet):


def listify(string, delimiter=','):
    l = []
    for ele in string.split(delimiter):
        l.append(ele.strip())
    return l


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
        '''
            recorded:   file 
            idx:        int
            previous_stream:  list<str>

            return 
        '''
        # print(request.FILES)
        # print(request.data)
        file = request.FILES['recorded']
        idx = int(request.data.get('idx', [0])[0])


        date  = datetime.today().strftime('%Y-%m-%d')
        dir = os.path.join(MEDIA_ROOT, date)
        os.makedirs(dir, exist_ok=True)
        
        fs = FileSystemStorage(dir)
        filename = fs.save(file.name, file)
        uploaded_file_url = fs.url(filename)
        file_full_path = os.path.join(dir, filename)
        

        #*************
        file_full_path = r'D:\Document\RUPP\Fourth Year\Semester 1\Project Practicum\Practice\Musics\Khmer Songs - Sampling\4s\សង្សារចាស់ Ver.wav'

        if idx != 0: 
            previous_stream = request.data.getlist('previous_stream', [])
            previous_stream = listify(previous_stream[0])
            previous_stream.append(filename)
            print(previous_stream)
            file_full_path = concat_song( dir, previous_stream, os.path.join(dir, filename) )

        if file_full_path is None: 
            return Response(status=status.HTTP_404_NOT_FOUND )

        #get db connection
        print(file_full_path)
        conn = DatabaseHandler.connect()
        result, total, std, mean = util.classify_song(file_full_path)
        if result is not None and len(result) > 0: 
            # result = {k: v for k, v in list(result.items())[:10]} #get first 10 items
            result = [v for k, v in list(result.items())[:10] ] #get first 10 items
        result = {'result': result}
        result['total_fingerprints'] = total
        result['std'] = std
        result['mean'] = mean
        print(result)

        return Response(status=status.HTTP_200_OK, data=result )

    

class SongView(views.APIView):
    querySet = Song.objects.all()
    serializer_class = SongSerializer

    def get(self, request, key=None):
        print(request)
        return Response('Hello world')