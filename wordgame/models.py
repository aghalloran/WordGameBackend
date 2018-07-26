from django.db import models
from django.contrib.auth.models import User
from collections import defaultdict
import hashlib
from django.db.models.signals import post_save
from tastypie.models import create_api_key

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    points = models.IntegerField(null=True,blank=True,default=0)
    streak = models.IntegerField(null=True,blank=True,default=0)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
models.signals.post_save.connect(create_api_key, sender=User)

# Create your models here.
class Round(models.Model):
    game_uid = models.CharField(max_length=75,null=True,blank=True)
    word = models.CharField(max_length=75,null=True,blank=True)
    players = models.ManyToManyField(User)
    round_number = models.IntegerField(null=True,blank=True)
    date_round_started = models.DateTimeField(null=True,blank=True)
    date_game_started = models.DateTimeField(null=True,blank=True)
    longest_streak = models.IntegerField(null=True,blank=True)
    has_answer = models.BooleanField(default=False)
    next_round = models.OneToOneField('self',
                                      null=True,
                                      blank=True,
                                      related_name='prev_round')
    
    def __unicode__(self):
        rstring = ''
        rstring += 'id='+str(self.id)
        rstring += ' guid='+str(self.game_uid)
        rstring += ' round='+str(self.round_number)
        return rstring

    def has_submitted_answer(self,user):
        state = self.playerroundstate_set.all().filter(player__username=user.username)
        if not state:
            return False

        return state.iterator().next().answer

    def get_round(self, number):
        round_qs = Round.objects.all().filter(game_uid__exact=self.game_uid,
                                   round_number__exact=number)
        if not round_qs:
            return None

        return round_qs.iterator().next()


    def get_next_round(self):
        return self.get_round(self.round_number+1)

    def get_previous_round(self):
        return self.get_round(self.round_number-1)

    def are_all_answers_submitted(self):
        num_players = self.players.count()
        round_states = self.playerroundstate_set.all()
        answer_count = 0
        for rs in round_states:
            if rs.answer:
                answer_count += 1

        if answer_count == num_players:
            return True

        return False

    def calc_streak(self):
        words = [prs.answer for prs in self.playerroundstate_set.all()]
        d = defaultdict(int)
        for word in words:
            d[word] += 1
        for entry in d:
            if d[entry] > 1:
                return self.longest_streak + 1
        return 0

    def calc_points(self,user):
        prs = self.playerroundstate_set.all().filter(player__username=user.username).iterator().next()
        points = -1
        for state in self.playerroundstate_set.all():
            if prs.answer == state.answer:
                points += 1
        return points

    def calc_guid(self):
        m = hashlib.sha1()
        m.update(self.word)
        m.update(str(self.date_game_started))
        m.update(str(self.date_round_started))
        m.update(str(self.round_number))
        m.update(str(self.players.all()))
        return m.hexdigest()

class PlayerGameScore(models.Model):
    player_total = models.IntegerField(null=True,blank=True,default=0)

    def __unicode__(self):
        rstring = ''
        rstring += 'player_total='+str(self.player_total)
        return rstring

class PlayerRoundState(models.Model):
    player = models.ForeignKey(User)
    round = models.ForeignKey(Round)
    game_score = models.ForeignKey(PlayerGameScore)
    answer = models.CharField(max_length=75)
    is_round_active = models.BooleanField()
    has_seen_results = models.BooleanField()
    point_total = models.IntegerField(null=True,blank=True,default=0)

    def __unicode__(self):
        rstring = ''
        rstring += 'id='+str(self.id)
        rstring += ' player='+str(self.player)
        rstring += ' active='+str(self.is_round_active)
        return rstring

    def calc_points(self):
        return self.round.calc_points(self.player)
