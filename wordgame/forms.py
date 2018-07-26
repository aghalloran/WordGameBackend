from django import forms
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from wordgame.models import Round, PlayerRoundState 
from random import choice
from wordlist import words

class CreateGameForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        self.the_user = kwargs.pop('user')
        super(CreateGameForm, self).__init__(*args, **kwargs)

    player1 = forms.RegexField(label='Player username 1',
                               max_length=30,
                               regex=r'[\w.@+-]+$',
                               error_messages={'invalid':'The username may contain only letters and numbers.'})
    player2 = forms.RegexField(label='Player username 2',
                               max_length=30,
                               regex=r'[\w.@+-]+$',
                               required=False,
                               error_messages={'invalid':'The username may contain only letters and numbers.'})
    player3 = forms.RegexField(label='Player username 3',
                               max_length=30,
                               regex=r'[\w.@+-]+$',
                               required=False,
                               error_messages={'invalid':'The username may contain only letters and numbers.'})
    player4 = forms.RegexField(label='Player username 4',
                               max_length=30,
                               regex=r'[\w.@+-]+$',
                               required=False,
                               error_messages={'invalid':'The username may contain only letters and numbers.'})

    class Meta:
        model = Round
        fields = ('player1','player2','player3','player4')

    def cleanuser(self,username):
        if username == '':
            return None
        
        user_found = User.objects.filter(username__iexact=username)
        if user_found.count() < 1:
            raise forms.ValidationError('Could not find a user with that username.')
        return user_found

    def clean_player1(self):
        username = self.cleaned_data.get('player1','')
        return self.cleanuser(username)

    def clean_player2(self):
        username = self.cleaned_data.get('player2','')
        return self.cleanuser(username)

    def clean_player3(self):
        username = self.cleaned_data.get('player3','')
        return self.cleanuser(username)

    def clean_player4(self):
        username = self.cleaned_data.get('player4','')
        return self.cleanuser(username)

    def save(self, commit=True):
        roundObj = super(CreateGameForm, self).save(commit=False)
        roundObj.word = choice(words)
        roundObj.date_started = timezone.now()
        roundObj.round_number = 1
        roundObj.longest_streak = 0
        roundObj.save()
        roundObj.players.add(self.the_user)
        roundObj.playerroundstate_set.create(player=self.the_user,
                                             round=roundObj,
                                             answer='',
                                             is_round_active=True,
                                             has_seen_results=False,
                                             point_total=0)
        if self.cleaned_data['player1'] is not None:
            p1 = self.cleaned_data['player1'].iterator().next() 
            roundObj.players.add(p1)
            roundObj.playerroundstate_set.create(player=p1,
                                                 round=roundObj,
                                                 answer='',
                                                 is_round_active=True,
                                                 has_seen_results=False,
                                                 point_total=0)
        if self.cleaned_data['player2'] is not None:
            p2 = self.cleaned_data['player2'].iterator().next() 
            roundObj.players.add(p2)
            roundObj.playerroundstate_set.create(player=p2,
                                                 round=roundObj,
                                                 answer='',
                                                 is_round_active=True,
                                                 has_seen_results=False,
                                                 point_total=0)
        if self.cleaned_data['player3'] is not None:
            p3 = self.cleaned_data['player3'].iterator().next() 
            roundObj.players.add(p3)
            roundObj.playerroundstate_set.create(player=p3,
                                                 round=roundObj,
                                                 answer='',
                                                 is_round_active=True,
                                                 has_seen_results=False,
                                                 point_total=0)
        if self.cleaned_data['player4'] is not None:
            p4 = self.cleaned_data['player4'].iterator().next() 
            roundObj.players.add(p4)
            roundObj.playerroundstate_set.create(player=p4,
                                                 round=roundObj,
                                                 answer='',
                                                 is_round_active=True,
                                                 has_seen_results=False,
                                                 point_total=0)
        
        roundObj.game_uid = roundObj.calc_guid()
        roundObj.save()
        return roundObj 

class SubmitAnswerForm(forms.Form):
 
    def __init__(self, *args, **kwargs):
        self.the_user = kwargs.pop('user')
        super(SubmitAnswerForm, self).__init__(*args, **kwargs)
    
    answer = forms.CharField(label='Your first thought',
                             max_length=75)

    def clean_answer(self):
        the_answer = self.cleaned_data.get('answer')
        return the_answer
