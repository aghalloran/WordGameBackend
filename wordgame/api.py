from tastypie.resources import ModelResource
from wordgame.models import Round, PlayerRoundState, UserProfile
from wordgame.models import PlayerGameScore
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authentication import Authentication
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from wordgame.wordlist import words
from random import choice
from django.utils import timezone
from tastypie.bundle import Bundle
import hashlib

class UserResource(ModelResource):
    userprofile = fields.OneToOneField('wordgame.api.UserProfileResource',
                                       attribute='userprofile',
                                       full=True,
                                       null=True,
                                       blank=True)

    class Meta:
        queryset = User.objects.all()
        resource_name = 'players'
#        fields = ['username','resource_uri']
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        filtering = {
            'username': ALL_WITH_RELATIONS,
        }
        
    def obj_create(self, bundle, request=None, **kwargs):
        
        if bundle.data['username'] == '':
            m = hashlib.sha1()
            m.update(str(timezone.now()))
            m.update(bundle.data['password'])
            m.update(bundle.data['email'])
            m.update(choice(words))
            bundle.data['username'] = '_'.join(['ftg_user',m.hexdigest()])
      
        #import pdb; pdb.set_trace()

        try:
            #user_check = User.objects.get(username__exact = bundle.data['username'])
            obj = self.obj_get(request, username=bundle.data['username'])
            #The user exists, now check the password
            user = authenticate(username=bundle.data['username'], password=bundle.data['password'])
            if user is None:
                raise BadRequest('The user exists but the password does not match')
            else:
                bundle = self.build_bundle(obj=obj, request=request)
        except ObjectDoesNotExist:
            #The user does not exist, try to create it
            try:
                bundle = super(UserResource, self).obj_create(bundle, request, **kwargs)
                bundle.obj.set_password(bundle.data.get('password'))
                bundle.obj.save()
            #Theoretically this exception should never be thrown because we already checked that it doesnt exist
            except IntegrityError:
                raise BadRequest('That username already exists')
        return bundle

class UserProfileResource(ModelResource):
    user = fields.ToOneField(UserResource,'user')
    points = fields.IntegerField(attribute='points', readonly=True, 
                                 null=True, blank=True)
    streak = fields.IntegerField(attribute='streak', readonly=True,
                                 null=True, blank=True)

    class Meta:
        queryset = UserProfile.objects.all()
        resource_name = 'userprofile'

class RoundResource(ModelResource):
    players = fields.ManyToManyField(UserResource, 
                                     attribute='players',
                                     full=False)
    states = fields.ManyToManyField('wordgame.api.StateResource',
                                    attribute='playerroundstate_set',
                                    full=True,
                                    blank=True,
                                    null=True)
    next_round = fields.OneToOneField('wordgame.api.RoundResource', 
                                      attribute='next_round',
                                      full=False,
                                      null=True,
                                      blank=True,
                                      readonly=True)
    prev_round = fields.OneToOneField('wordgame.api.RoundResource', 
                                      attribute='prev_round',
                                      full=False,
                                      null=True,
                                      blank=True,
                                      readonly=True)
    date_round_started = fields.DateTimeField(attribute='date_round_started',
                                        null=True,
                                        blank=True,
                                        readonly=True)
    date_game_started = fields.DateTimeField(attribute='date_game_started',
                                        null=True,
                                        blank=True,
                                        readonly=True)
    word = fields.CharField(attribute='word', readonly=True,null=True,
                            blank=True)
    round_number = fields.IntegerField(attribute='round_number', readonly=True,
                                       null=True,blank=True)
    game_uid = fields.CharField(attribute='game_uid', readonly=True,
                                null=True,blank=True)
    id = fields.IntegerField(attribute='id', readonly=True, 
                             null=True,blank=True)
    resource_uri = fields.CharField(attribute='resource_uri', readonly=True,
                                    null=True,blank=True)
    longest_streak = fields.IntegerField(attribute='longest_streak',
                                         readonly=True, null=True, blank=True)


    class Meta:
        queryset = Round.objects.all()
        resource_name = 'rounds'
        always_return_data = True
        authentication = BasicAuthentication()
        authorization = Authorization()
        #fields = ['date_started','game_uid','players','resource_uri',
        #          'round_number','longest_streak']

        filtering = {
            'players': ALL_WITH_RELATIONS,
            'states': ALL_WITH_RELATIONS,
        }

    def create_state(self, round_obj, player, game_score):
        state = PlayerRoundState()
        state.answer = ''
        state.has_seen_results = False
        state.is_round_active = True
        state.player = player
        state.point_total = 0
        state.round = round_obj
        state.game_score = game_score
        state.save()
        return state

    def create_next_round(self, obj):
        new_round = Round()
        new_round.word = choice(words)
        new_round.date_game_started = obj.date_game_started
        new_round.date_round_started = timezone.now()
        new_round.game_uid = obj.game_uid
        new_round.round_number = obj.round_number+1
        new_round.save()

        for state in obj.playerroundstate_set.all():
            self.create_state(new_round,state.player,state.game_score)

        for player in obj.players.all(): 
            new_round.players.add(player)

        new_round.save()
        return new_round 


    def obj_create(self, bundle, request=None, **kwargs):
        player_list = bundle.data['players'] 
        bundle = super(RoundResource, self).obj_create(bundle, request, 
                       **kwargs)
        bundle.obj.word = choice(words)
        bundle.obj.date_game_started = kwargs.get('date_game_started',
                                                   timezone.now())
        bundle.obj.date_round_started = timezone.now()
        bundle.obj.round_number = kwargs.get('round_number',1)
        bundle.obj.game_uid = kwargs.get('game_uid',bundle.obj.calc_guid())
        bundle.obj.save()
        
        for player in bundle.obj.players.all():
            game_score = PlayerGameScore()
            game_score.player_total = 0
            game_score.save()
            state = self.create_state(bundle.obj,player,game_score)
        
        bundle.obj.save()
        #import pdb; pdb.set_trace()
        if kwargs.get('game_uid') is None:
            new_round = self.create_next_round(bundle.obj)
            bundle.obj.next_round = new_round 
            bundle.obj.save()

        return bundle

    def obj_update(self, bundle, request=None, skip_errors=False, **kwargs):
        bundle = super(RoundResource, self).obj_update(bundle, request,
                                                       skip_errors, **kwargs)
        return bundle

    def get_object_list(self, request):
        return super(RoundResource, self).get_object_list(request)

    def obj_get_list(self, request=None, **kwargs):
        return super(RoundResource, self).obj_get_list(request,**kwargs)

    def obj_get(self, request=None, **kwargs):
        obj = super(RoundResource, self).obj_get(request, **kwargs)
        if obj.has_answer and obj.next_round is None:
            nr = self.create_next_round(obj)
            obj.next_round = nr
            obj.save()
       
        return obj

class GameScoreResource(ModelResource):
    player_total = fields.IntegerField(attribute='player_total', readonly=True,
                                       null=True, blank=True)

    class Meta:
        queryset = PlayerGameScore.objects.all()
        resource_name = 'scores'
        authentication = BasicAuthentication()
        authorization = Authorization()

class StateResource(ModelResource):
    player = fields.ForeignKey(UserResource, 'player',full=False)
    round = fields.ForeignKey(RoundResource, 'round')
    point_total = fields.IntegerField(attribute='point_total', readonly=True, 
                                 null=True, blank=True)
    game_score = fields.ForeignKey(GameScoreResource, 'game_score',full=True)

    class Meta:
        queryset = PlayerRoundState.objects.all()
        resource_name = 'states'
        always_return_data = True
        authentication = BasicAuthentication()
        authorization = Authorization()
        #fields = ['answer','player','point_total']        
        
        filtering = {
            'answer': ALL_WITH_RELATIONS,
            'is_round_active': ALL_WITH_RELATIONS,
            'player': ALL_WITH_RELATIONS,
        }

    def obj_create(self, bundle, request=None, **kwargs):
        bundle = super(StateResource, self).obj_create(bundle, request, 
                                                       **kwargs)
        return bundle

    def obj_update(self, bundle, request=None, skip_errors=False, **kwargs):
#        import pdb; pdb.set_trace()
        bundle = super(StateResource, self).obj_update(bundle, request,
                                                       skip_errors, **kwargs)
        for state in bundle.obj.round.playerroundstate_set.all():
            if bundle.obj.answer == state.answer and bundle.obj != state:
                bundle.obj.point_total += 1
                bundle.obj.game_score.player_total += 1
                bundle.obj.player.userprofile.points += 1
                state.point_total += 1
                state.game_score.player_total += 1
                state.player.userprofile.points += 1                
                state.save()
                state.player.userprofile.save()
                state.game_score.save()
        
        if bundle.obj.answer:
            bundle.obj.round.has_answer=True
            bundle.obj.round.save()

        bundle.obj.save()
        bundle.obj.player.userprofile.save()
        bundle.obj.game_score.save()

        return bundle
