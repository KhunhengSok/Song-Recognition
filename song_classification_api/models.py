from django.db import models

# Create your models here.
class Song(models.Model):
    id = models.AutoField(primary_key=True, db_index=True, editable=False,  )
    name = models.CharField(max_length=60)
    artist = models.CharField(max_length =50)
    album = models.CharField(max_length =50, default=None)
    file_location = models.CharField(max_length=100)
    total_fingerprints = models.IntegerField()

    class Meta:
        db_table  = 'tbl_songs'

    def __str__(self):
        return self.name

class SongFingerprint(models.Model):
    id = models.AutoField(primary_key=True,  db_index=True, editable=False )
    hash = models.CharField(max_length = 35, db_index=True)
    offset = models.IntegerField()
    song = models.ForeignKey(Song, on_delete=models.CASCADE, db_index=True,)
    
    class Meta:
        db_table  = 'tbl_song_fingerprints'

    def __str__(self):
        return self.hash


# class Artist(models.Models):
#     artist_id = models.IntegerField(primary_key=True, )
#     name = models.CharField(max_length =50)

#     def __str__(self):
#         sreturn self.name
