from django.shortcuts import render_to_response, get_object_or_404
from polls.models import Poll, Choice
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from accounts.forms import RegistrationForm
from django.contrib.auth import authenticate, login

def registration(request):
    if request.method == 'POST': 
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            user = authenticate(username=new_user.username,
                                password=form.clean_password2())
            if user is not None:
                login(request, user)
            else:
                pass #TODO:Put log statement here
            return HttpResponseRedirect('/wordgame/main/')
    else:
        form = RegistrationForm()

    return render_to_response('accounts/registration.html',
                              {'form':form},
                              context_instance=RequestContext(request))

