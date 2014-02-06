from django.db import models
from django.db.models.signals import post_save

# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length=100)
    rating = models.IntegerField()
    live_rating = models.IntegerField()
    favorite_color = models.IntegerField()
    def __unicode__(self):
    	return self.name
    def calculate_rating(self, opponent_rating, result):
        change = result * (self.live_rating / opponent_rating) * 10
        self.live_rating = self.live_rating + change
        return change 

class Game(models.Model):
    winner = models.ForeignKey(Player, related_name="won_games")
    loser = models.ForeignKey(Player, related_name="lost_games")
    datetime = models.DateTimeField(auto_now=True)
    under_table = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    def __unicode__(self):
        return self.winner.name + " vs. " + self.loser.name + " " + self.datetime.strftime("%Y-%m-%d")
    def calculate_ratings(self, instance, **kwargs):
        winner_rating = winner.live_rating
        winner.calculate_rating(opponent.live_rating, 1)
        loser.calculate_rating(winner_rating, -1)
    post_save.connect(calculate_ratings)
