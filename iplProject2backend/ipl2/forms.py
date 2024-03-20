from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserInfo
from django.contrib.auth.models import User  # Import Django's User model
from django.contrib.auth.forms import PasswordResetForm
from datetime import datetime

class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ("username", "email", "name", "password1", "password2")
        error_messages = {
            'username': {
                'required': 'This field is required.',
            },
            'password1': {
                'min_length': 'Your password must contain at least 8 characters.',   
            },
        }

    def save(self, commit=True):
        user = super(RegisterUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create UserInfo instance
            UserInfo.objects.create(
                user=user,
                username=user.username,
                name=self.cleaned_data['name'],
                email=user.email,
                created_on=datetime.now()
            )
        return user


from .models import MatchInfo

class MatchInfoForm(forms.ModelForm):
    matchID = forms.IntegerField(label='Match ID', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Match ID'}))
    
    class Meta:
        model = MatchInfo
        fields = ('matchID', 'matchdate', 'matchtime', 'teamA', 'teamB', 'winner_team', 'status', 'playerofmatch', 'mostrunsplayer', 'mostwickettaker')
        labels = {
            'matchdate': 'Match Date',
            'matchtime': 'Match Time',
            'teamA': 'Team A',
            'teamB': 'Team B',
            'winner_team': 'Winner Team',
            'status': 'Status',
            'playerofmatch': 'Player of the Match',
            'mostrunsplayer': 'Player with Most Runs',
            'mostwickettaker': 'Player with Most Wickets',
        }
        widgets = {
            'matchdate': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Match Date'}),
            'matchtime': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Match Time'}),
            'teamA': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Team A'}),
            'teamB': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Team B'}),
            'winner_team': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Winner Team'}),
            'status': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Status'}),
            'playerofmatch': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Player of the Match'}),
            'mostrunsplayer': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Player with Most Runs'}),
            'mostwickettaker': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Player with Most Wickets'}),
        }

#for password reset
class CustomPasswordResetForm(PasswordResetForm):
     username = forms.CharField(max_length=254, label='Username')

     class Meta :
         model =User
         fields=("username","email")
  
from .models import LbRegistrationTable

class LbRegistrationForm(forms.ModelForm):
    class Meta:
        model = LbRegistrationTable
        fields = ['uid', 'leaderboardname', 'password']
        labels = {
            'uid': 'User ID',
            'leaderboardname': 'Leaderboard Name',
            'password': 'Password'
        }
        widgets = {
            'password': forms.PasswordInput()
        }

from .models import SubmissionsInfo5

class PredictionForm(forms.ModelForm):
    class Meta:
        model = SubmissionsInfo5
        fields = ['smatch', 'predictedteam', 'predictedpom', 'predictedmr', 'predictedmwk']
