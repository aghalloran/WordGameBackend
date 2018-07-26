from django.shortcuts import render_to_response, get_object_or_404
from wordgame.models import Round, PlayerRoundState
from wordgame.forms import CreateGameForm, SubmitAnswerForm
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from wordgame.wordlist import words
from random import choice

@login_required
def index(request):
    round_states = PlayerRoundState.objects.all().filter(player__username=request.user.username,is_round_active=True)
    return render_to_response('wordgame/index.html',
                              {'round_states':round_states},
                              context_instance=RequestContext(request))

@login_required
def create_game(request):
    if request.method == 'POST':
        the_user = User.objects.filter(username__iexact=request.user.username).iterator().next()
        form = CreateGameForm(request.POST,user=the_user)
        if form.is_valid():
            new_game = form.save()
            return HttpResponseRedirect('/wordgame/main/')
    else:
        form = CreateGameForm(user=request.user)
    
    return render_to_response('wordgame/create.html',
                              {'form':form},
                              context_instance=RequestContext(request))

@login_required
def create_game_random(request):
    return render_to_response('wordgame/create_random.html',
                              context_instance=RequestContext(request))

@login_required
def prep_round(request, round_id):
    old_round = get_object_or_404(Round, pk=round_id)
    next_round = old_round.get_next_round()

    if not next_round:
        new_word = choice(words)
        streak = old_round.calc_streak()
        next_round = Round.objects.create(game_uid=old_round.game_uid,
                                     word=new_word,
                                     round_number=old_round.round_number+1,
                                     date_started=timezone.now(),
                                     longest_streak=streak)
        for p in old_round.players.all():
            next_round.players.add(p)
        for ps in old_round.playerroundstate_set.all():
            points = ps.point_total + ps.calc_points()
            next_round.playerroundstate_set.create(player=ps.player,
                                              round=next_round,
                                              answer='',
                                              is_round_active=False,
                                              has_seen_results=False,
                                              point_total=points)
    
    old_state = old_round.playerroundstate_set.all().filter(player__username=request.user.username).iterator().next()
    next_state = next_round.playerroundstate_set.all().filter(player__username=request.user.username).iterator().next()

    old_state.is_round_active = False
    old_state.has_seen_results = True
    old_state.save()

    next_state.is_round_active = True
    next_state.save()

    form = SubmitAnswerForm(user=request.user)

    return HttpResponseRedirect('/wordgame/main/')
    """ This does not work for some reason.
    return render_to_response('/wordgame/round/'+str(next_round.id)+'/',
                              {'the_round':next_state.round,
                               'has_answer':next_state.answer,
                               'the_answer':next_state.answer,
                               'form':form},
                               context_instance=RequestContext(request))
    """

@login_required
def play_game(request, playerroundstate_id):
    prs = get_object_or_404(PlayerRoundState, pk=playerroundstate_id)
    
    if request.method == 'GET': 
        form = SubmitAnswerForm(user=request.user)
        return render_to_response('wordgame/play_game.html',
                                  {'the_round':prs.round,
                                   'has_answer':prs.answer,
                                   'the_answer':prs.answer,
                                   'form':form},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        the_user = User.objects.filter(username__iexact=request.user.username).iterator().next()
        form = SubmitAnswerForm(request.POST,user=the_user)
        if form.is_valid():
            prs.answer = form.cleaned_data['answer']
            prs.save() 
            return HttpResponseRedirect('/wordgame/main/')
    else:
        form = SubmitAnswerForm(user=request.user)

    return render_to_response('wordgame/play_game.html',
                              {'the_round':prs.round,
                               'has_answer':prs.answer,
                               'the_answer':prs.answer,
                               'form':form},
                              context_instance=RequestContext(request))
 
