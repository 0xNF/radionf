from django.db import models


class Song(models.Model):
    Id = models.TextField("Id", primary_key=True)
    Kind = models.TextField("kind")
    JsonData = models.TextField("jsondata")

    @classmethod
    def createSong(self, song_id, json_data):
        song = self.create(Id = song_id, jsonData = json_data)
        return song

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Id', 'Kind'], name='unique_kind_id')
        ]

class History(models.Model):
    Timestamp = models.DateTimeField("timestamp", primary_key=True)
    Song = models.ForeignKey(Song, on_delete=models.CASCADE)

    @classmethod
    def createHistory(self, timestamp, song):
        h = self.create(Timestamp = timestamp, Song = song)
        return h