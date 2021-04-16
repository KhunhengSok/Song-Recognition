from django.db import models

# Create your models here.
class Song(models.Model):
    id = models.IntegerField(primary_key=True, db_index=True, editable=False )
    name = models.CharField(max_length=60)
    artist = models.CharField(max_length =50)
    file_location = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class SongFingerprint(models.Model):
    id = models.IntegerField(primary_key=True, db_index=True, editable=False )
    hash = models.CharField(max_length = 35, db_index=True)
    offset = models.IntegerField()
    song_id = models.ForeignKey(Song, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.hash


# class Artist(models.Models):
#     artist_id = models.IntegerField(primary_key=True, )
#     name = models.CharField(max_length =50)

#     def __str__(self):
#         sreturn self.name
