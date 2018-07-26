from django import forms
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

class RegistrationForm(forms.ModelForm):
    username = forms.RegexField(label='Username',
                                max_length=30,
                                regex=r'[\w.@+-]+$',
                                error_messages={'invalid':'The username may contain only letters and numbers.'})
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    email = forms.EmailField(label="Email", max_length=75)
    
    class Meta:
        model = User
        fields = ('username','email')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError('The two passwords must match.')
        return password2

    def clean_email(self):
        email = self.cleaned_data['email']
        users_found = User.objects.filter(email__iexact=email)
        if len(users_found) >= 1:
            raise forms.ValidationError('A user with that email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        users_found = User.objects.filter(username__iexact=username)
        if users_found.count() >= 1:
            raise forms.ValidationError('A user with that username already exists.')
        return username

    def save(self, commit=True, domain_override=None, use_https=False):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password2'])
        user.email = self.cleaned_data['email']
        user.is_active = True
        if commit:
            user.save()
        return user
