from django.conf.urls import patterns, include, url
from wordgame.api import RoundResource, UserResource, StateResource
from wordgame.api import GameScoreResource
from wordgame.api import UserProfileResource
from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(RoundResource())
v1_api.register(UserResource())
v1_api.register(StateResource())
v1_api.register(UserProfileResource())
v1_api.register(GameScoreResource())

urlpatterns = patterns('',
    url(r'^main/$','wordgame.views.index'),
    url(r'^create/$','wordgame.views.create_game'),
    url(r'^prepround/(?P<round_id>\d+)/$','wordgame.views.prep_round'),
    url(r'^round/(?P<playerroundstate_id>\d+)/$','wordgame.views.play_game'),
    url(r'^api/',include(v1_api.urls)),
)
