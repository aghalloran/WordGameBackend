from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^login/$','django.contrib.auth.views.login',
        {'template_name':'accounts/login.html'}),
    url(r'^logout/$','django.contrib.auth.views.logout',
         {'next_page':'/wordgame/main/'}),
    url(r'^password_change/$','django.contrib.auth.views.password_change',
        {'template_name':'accounts/password_change.html'}),
    url(r'^password_reset/$','django.contrib.auth.views.password_reset',
        {'template_name':'accounts/password_reset_form.html',
        'email_template_name':'accounts/password_reset_email.html'}),
    url(r'^registration/$','accounts.views.registration'),
)

