from datetime import timezone
import json
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import  MatchInfoForm, RegisterUserForm 
from django.core.serializers import serialize
from .models import SubmissionsInfo5, UserInfo, LbParticipationTable, LbRegistrationTable, MatchInfo, TeamInfo, PlayerInfo
from rest_framework.views import APIView
from .serializers import MatchInfoSerializer, TeamInfoSerializer, SubmissionsInfo5Serializer
from django.db.models import Count
from django.forms.models import model_to_dict
from django.utils.decorators import method_decorator
from django.views import View
from datetime import datetime
from django.utils import timezone
from pytz import timezone as pytz_timezone

from django.contrib.auth import views as auth_views
from django import forms
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import PasswordResetForm
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .forms import CustomPasswordResetForm 
from django.contrib.sites.shortcuts import get_current_site  
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.template.loader import render_to_string  
from .tokens import account_activation_token  
from django.contrib.auth.models import User  
from django.core.mail import EmailMessage  
from django.contrib.auth import get_user_model
from django.http import HttpResponse


@api_view(['GET'])
def home(request):
    # Retrieve all MatchInfo objects
    matches = MatchInfo.objects.all()
    
    # Serialize the queryset
    serializer = MatchInfoSerializer(matches, many=True)
    
    total_users = UserInfo.objects.count()
    # Return the serialized data as JSON response
    return Response({'matches': serializer.data, 'total_users': total_users})
    
@method_decorator(csrf_exempt, name='dispatch')
class RegisterUserView(View):
    def post(self, request):
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            # Create a RegisterUserForm instance with the received data
            form = RegisterUserForm(data)
            if form.is_valid():
                # Save the form data to create a new user
                user = form.save()
                # Access UserInfo related to the user
                user_info = user.userinfo

                # Create entries in LbParticipationTable for the existing Global and Weekly Leaderboards and the newly registered user
                global_leaderboard = LbRegistrationTable.objects.get(leaderboardname='Global')
                LbParticipationTable.objects.create(lid=global_leaderboard, username=user_info)

                weekly_leaderboard = LbRegistrationTable.objects.get(leaderboardname='Weekly')
                LbParticipationTable.objects.create(lid=weekly_leaderboard, username=user_info)

                # Return success message and user data as JSON response
                user_data = model_to_dict(user)

                return JsonResponse({'success': True, 'message': 'User registered successfully', 'user': user_data}, status=201)  # Status 201 indicates resource creation
            else:
                # If form is not valid, return validation errors as JSON response
                return JsonResponse({'error': 'Username or Email is already in use!'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        except LbRegistrationTable.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Leaderboard does not exist'}, status=404)

    def get(self, request):
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405) 

@method_decorator(csrf_exempt, name='dispatch')
class LoginUserView(View):
    def post(self, request):
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)

            username = data.get('username')
            password = data.get('password1')

            # Perform authentication
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                # Serialize user data
                user_data = {
                    'username': user.username,
                    'email': user.email,
                    # Add more fields as needed
                }
                return JsonResponse({'user': user_data}, status=200)
            else:
                return JsonResponse({'error': 'Invalid username or password'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    def get(self, request):
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def logout_user(request):
    logout(request)
    messages.success(request, ("Logged Out Successfully!! "))
    return redirect('home')

class UserSubmissions(APIView):
    def get(self, request, username):
        # Fetch all submissions for the specified user
        user_submissions = SubmissionsInfo5.objects.filter(username=username).order_by('smatch_id')

        # Serialize the data to JSON format
        serialized_data = SubmissionsInfo5Serializer(user_submissions, many=True).data

        # Return the serialized data as a JSON response
        return JsonResponse({'username': username, 'submissions': serialized_data})

class MatchInfoList(APIView):
    def get(self, request):
        # Retrieve past matches (status=1) and order them by match date
        past_matches = MatchInfo.objects.filter(status=1).order_by('-matchdate')[:5]
        
        # Serialize past matches
        past_matches_serializer = MatchInfoSerializer(past_matches, many=True)
        # Retrieve upcoming matches (status=0) and order them by match date
        upcoming_matches = MatchInfo.objects.filter(status=0).order_by('matchdate')[:9]
        
        # Serialize upcoming matches
        upcoming_matches_serializer = MatchInfoSerializer(upcoming_matches, many=True)
        # Return the serialized data as JSON response

        return Response({'past_matches': past_matches_serializer.data, 'upcoming_matches': upcoming_matches_serializer.data})

def leaderboard2(request):
    leaderboards = LbRegistrationTable.objects.all()

    # Get the selected leaderboard ID from the URL parameters
    selected_leaderboard_id = request.GET.get('selected_leaderboard')
    # Initialize an empty queryset for user_list
    user_list = UserInfo.objects.none()
    # Initialize selected_leaderboard
    selected_leaderboard = None

    # Filter users based on the selected leaderboard if a leaderboard is selected
    if selected_leaderboard_id:
        try:
            selected_leaderboard_id = int(selected_leaderboard_id)
            # Retrieve the usernames of users who have participated in the selected leaderboard
            usernames = LbParticipationTable.objects.filter(lid_id=selected_leaderboard_id).values_list('username__username', flat=True)
            # Filter user_list based on the usernames obtained
            user_list = UserInfo.objects.filter(username__in=usernames)
            # Get the selected leaderboard object
            selected_leaderboard = LbRegistrationTable.objects.get(pk=selected_leaderboard_id)
            if selected_leaderboard.leaderboardname == 'Weekly':
                user_list = user_list.order_by('-score2', 'username')
            else:
                user_list = user_list.order_by('-score1', 'username')
        except (ValueError, LbRegistrationTable.DoesNotExist):
            pass
    else:
        # If no leaderboard is selected or if 'Global' is selected by default, display users for 'Global' leaderboard
        global_leaderboard = leaderboards.filter(leaderboardname='Global').first()
        if global_leaderboard:
            usernames = LbParticipationTable.objects.filter(lid_id=global_leaderboard.pk).values_list('username__username', flat=True)
            user_list = UserInfo.objects.filter(username__in=usernames).order_by('-score1', 'username')
            selected_leaderboard = global_leaderboard

    # Assign ranks to users in user_list
    for rank, user_info in enumerate(user_list, start=1):
        user_info.rank = rank

    # Serialize the data to JSON format
    serialized_data = {
        'leaderboards': list(leaderboards.values()),  # Convert queryset to list of dictionaries
        'user_list': [{'rank': user_info.rank, 'username': user_info.username, 'score1': user_info.score1, 'score2': user_info.score2} for user_info in user_list],  # Include only necessary fields
        'selected_leaderboard': {
            'lid': selected_leaderboard.lid,  # Use the primary key field here
            'leaderboardname': selected_leaderboard.leaderboardname,
            # Add more fields as needed
        } if selected_leaderboard else None
    }

    # Return the serialized data as a JSON response
    return JsonResponse(serialized_data)

IST = pytz_timezone('Asia/Kolkata') 

@csrf_exempt
def predict1(request, match_id):
    if request.method == "POST":
        match = MatchInfo.objects.filter(matchID=match_id).first()
        if not match:
            return JsonResponse({'error': 'Match does not exist'}, status=400)
        
        else:
            current_time_ist = timezone.now().astimezone(IST)
        
            match_datetime_ist = timezone.make_aware(
                timezone.datetime.combine(match.matchdate, match.matchtime),
                timezone=IST
            )

            if current_time_ist >= match_datetime_ist:
                print("Time UP")
                return JsonResponse({'error': 'Prediction closed. Match has already started.'}, status=400)
        
            team_A = match.teamA
            team_B = match.teamB

            body_data = json.loads(request.body)
            predicted_winner_team = body_data.get('predicted_winner_team')
            predicted_player_of_match = body_data.get('predicted_player_of_the_match')
            predicted_most_runs_scorer = body_data.get('predicted_most_runs_scorer')
            predicted_most_wicket_taker = body_data.get('predicted_most_wicket_taker')
            username = body_data.get('username')

            current_user = UserInfo.objects.get(username=username)
            user_info = current_user  # Assign the actual UserInfo instance

            predicted_team_instance = TeamInfo.objects.get(teamname=predicted_winner_team)
            predicted_player_of_match_instance = PlayerInfo.objects.get(playerName=predicted_player_of_match)
            predicted_most_runs_scorer_instance = PlayerInfo.objects.get(playerName=predicted_most_runs_scorer)
            predicted_most_wicket_taker_instance = PlayerInfo.objects.get(playerName=predicted_most_wicket_taker)

            submission_time = timezone.now()

            existing_submission = SubmissionsInfo5.objects.filter(user=user_info, smatch=match).first()
            
            if existing_submission:
                # Update the existing submission data
                existing_submission.predictedteam = predicted_team_instance
                existing_submission.predictedpom = predicted_player_of_match_instance
                existing_submission.predictedmr = predicted_most_runs_scorer_instance
                existing_submission.predictedmwk = predicted_most_wicket_taker_instance
                existing_submission.updated_time = submission_time
                existing_submission.save()

            else:
                # Create a new submission
                submission = SubmissionsInfo5(
                    smatch=match,
                    predictedteam=predicted_team_instance,
                    predictedpom=predicted_player_of_match_instance,
                    predictedmr=predicted_most_runs_scorer_instance,
                    predictedmwk=predicted_most_wicket_taker_instance,
                    user=user_info,
                    username=username,
                    updated_time=submission_time,
                )
                submission.save()

            return JsonResponse({'success': True, 'message': 'Prediction submitted successfully'})

        return JsonResponse({'error': 'Match does not exist'}, status=400)
    # If the request method is not POST
    else:
        # Retrieve the match information
        match = MatchInfo.objects.filter(matchID=match_id).first()

        if match:
            # Fetch team names from the match
            team_A = match.teamA
            team_B = match.teamB

            # Filter players based on match_id and teams
            players_A = PlayerInfo.objects.filter(playerTeamNo=team_A, playing11status=1)
            players_B = PlayerInfo.objects.filter(playerTeamNo=team_B, playing11status=1)


            # Merge players from both teams
            all_players_data = [
                {'name': player.playerName, 'team': team_A.teamshortform} for player in players_A
            ] + [
                {'name': player.playerName, 'team': team_B.teamshortform} for player in players_B
            ]

            # Serialize team_A and team_B
            team_A_data = model_to_dict(team_A)
            team_B_data = model_to_dict(team_B)

            # Filter batsmen and bowlers based on enumeration data type
            batsmen_data = [{'name': player.playerName, 'team': team_A.teamshortform} for player in players_A if player.playerRole in [1, 3, 4]] + [{'name': player.playerName, 'team': team_B.teamshortform} for player in players_B if player.playerRole in [1, 3, 4]]
            bowlers_data = [{'name': player.playerName, 'team': team_A.teamshortform} for player in players_A if player.playerRole in [2, 3]] + [{'name': player.playerName, 'team': team_B.teamshortform} for player in players_B if player.playerRole in [2, 3]]

            match_status = match.status
            winner_team = match.winner_team
            player_of_match = match.playerofmatch.playerName if match.playerofmatch else None
            most_runs_player = match.mostrunsplayer.playerName if match.mostrunsplayer else None
            most_wickets_taker = match.mostwickettaker.playerName if match.mostwickettaker else None
            match_date = match.matchdate.strftime('%Y-%m-%d') if match.matchdate else None
            match_time = match.matchtime.strftime('%H:%M:%S') if match.matchtime else None

            # Return the JSON response with the merged data including match status
            return JsonResponse({
                'team_A': team_A_data,
                'team_B': team_B_data,
                'match_date': match_date,
                'match_time': match_time,
                'players': all_players_data,
                'batsmen': batsmen_data,
                'bowlers': bowlers_data,
                'match_status': match_status,
                'winner_team': winner_team.teamname if winner_team else None,
                'player_of_match': player_of_match,
                'most_runs_player': most_runs_player,
                'most_wickets_taker': most_wickets_taker,
            })

        # If the match does not exist
        return JsonResponse({'error': 'Match does not exist'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class LBParticipationView(View):
    def post(self, request):
        # Parse the request body to extract form data
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        leaderboardname = body_data.get('leaderboardname')
        password = body_data.get('password')
        username = body_data.get('username')  # Add username to form data
        
        try:
            leaderboard_obj = LbRegistrationTable.objects.get(leaderboardname=leaderboardname)
            if password == leaderboard_obj.password:
                # Fetch the logged-in user's username
                user = UserInfo.objects.get(username=username)
                # Check if the user already exists in the leaderboard
                if LbParticipationTable.objects.filter(lid=leaderboard_obj, username=user).exists():
                    return JsonResponse({'error': 'User already exists in the leaderboard'}, status=400)
                else:
                    # If user doesn't exist, create new entry in LbParticipationTable
                    lb_participation = LbParticipationTable.objects.create(lid=leaderboard_obj, username=user)
                    messages.success(request, 'Successfully participated in the leaderboard.')
                    return JsonResponse({'success': True})  # Respond with success
            else:
                return JsonResponse({'error': 'Incorrect password'}, status=400)
        except LbRegistrationTable.DoesNotExist:
            return JsonResponse({'error': 'Leaderboard does not exist'}, status=400)
        except UserInfo.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=400)

import string
import random

def suggest_password(request):
    # Define the character set for the password
    password_characters = string.ascii_letters + string.digits + "!@#$"

    # Generate a random 10-character password
    password = ''.join(random.choice(password_characters) for _ in range(10))

    # Return the generated password as a JSON response
    return JsonResponse({'password': password})

def control_panel(request):
    return render(request, 'ipl2/controlpanel.html')

def update_match2(request, match_id):
    match_info = MatchInfo.objects.get(pk=match_id)
    form = MatchInfoForm(request.POST or None, instance=match_info)

    if form.is_valid():
        form.save()

        #score_update1(request,match_id)
        score_update2(request,match_id)
        #revert_score_updates(match_id)
        #score_update2(request,match_id)

        messages.success(request, "Match details updated successfully!")
        return redirect('home')

    return render(request, 'ipl2/update_match2.html', {'match_info': match_info, 'form': form})

def score_update2(request, match_id):
    # Fetch the match information
    match = MatchInfo.objects.filter(matchID=match_id).first()##try to add status also
    match_id = int(match_id)

    # If the match exists, proceed with scoring
    if match:
        # DetermŚine the points awarded for correct predictions
        correct_winner_points = 1
        correct_predictions_points = 1

        # Define base points and multipliers
        base_correct_winner_points = 3
        base_correct_predictions_points = 2
        
        i=1

        # Multiply the base points with the multiplier based on the match set
        correct_winner_points = base_correct_winner_points * i
        correct_predictions_points = base_correct_predictions_points * i

        # Fetch submissions for the specified match and correct predicted team
        submissions = SubmissionsInfo5.objects.filter(smatch_id=match_id)

        # Update scores for each user who made correct predictions
        for submission in submissions:
            # Fetch the username from the submission
            un = submission.username
            
            # Fetch the user information using the username
            user_info = UserInfo.objects.filter(username=un).first()

            if user_info:

                # Update score1 and score2 for correct predicted team
                if submission.predictedteam == match.winner_team:
                    user_info.score1 += correct_winner_points
                    user_info.score2 += correct_winner_points

                # Update score1 for correct predicted playerofmatch, mostrunsplayer, mostwickettaker
                if submission.predictedpom == match.playerofmatch:
                    user_info.score1 += correct_predictions_points
                    user_info.score2 += correct_predictions_points
                if submission.predictedmr == match.mostrunsplayer:
                    user_info.score1 += correct_predictions_points
                    user_info.score2 += correct_predictions_points
                if submission.predictedmwk == match.mostwickettaker:
                    user_info.score1 += correct_predictions_points
                    user_info.score2 += correct_predictions_points

                # Save the updated user information
                user_info.save()

                # Add points for correct predicted team
                if submission.predictedteam == match.winner_team:
                    submission.score += correct_winner_points
                if submission.predictedpom == match.playerofmatch:
                    submission.score += correct_predictions_points
                if submission.predictedmr == match.mostrunsplayer:
                    submission.score += correct_predictions_points
                if submission.predictedmwk == match.mostwickettaker:
                    submission.score += correct_predictions_points
                # Save the submission
                submission.save()

    return render(request, 'ipl2/score_update_success.html')

def revert_score_updates(request,match_id):
    # Fetch the match information
    match = MatchInfo.objects.filter(matchID=match_id).first()

    if match:
        # Fetch submissions for the specified match and correct predicted team
        submissions = SubmissionsInfo5.objects.filter(smatch_id=match_id)

        # Iterate over submissions to revert changes
        for submission in submissions:
            # Fetch the user information
            user_info = submission.user
            # print(submission.score)
            # Revert score1 and score2 to previous values
            
            user_info.score1 -= submission.score
            # print(submission.score)
            user_info.score2 -= submission.score
            # print(submission.score)
            # Save the user information
            user_info.save()

            # Revert the submission score to 0
            submission.score = 0
            submission.save()
    return render(request, 'ipl2/revert_changes.html')

def reset_weekly_leaderboard(request):
    # Reset the score2 field of all users to 0
    UserInfo.objects.all().update(score2=0)

    return render(request, 'ipl2/reset_weekly_leaderboard.html')

from .forms import LbRegistrationForm

@login_required()
def lb_registration(request):
    if not request.user.is_superuser:
        messages.error(request, "Only superusers can create leaderboards.")
        return redirect('home')
    
    if request.method == "POST":
        form = LbRegistrationForm(request.POST)
        if form.is_valid():
            lb_info = form.save(commit=False)
            # Perform any additional processing or validation here
            lb_info.save()

            messages.success(request, "Leaderboard registered successfully!")
            return redirect('home')  # Redirect to the home page after successful registration
        else:
            messages.error(request, "Invalid form details. Please check and try again.")
            return redirect('home')  # Redirect to the home page with an error message

    else:
        form = LbRegistrationForm()

    return render(request, 'ipl2/lb_registration.html', {'form': form})


def activate(request, uidb64, token):  
    User = get_user_model()  
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None  
    if user is not None and account_activation_token.check_token(user, token):  
        user.is_active = True  
        user.save()  
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')  
    else:  
        return HttpResponse('Activation link is invalid!')

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm  
    template_name = 'ipl2/password_reset_form.html'  # Specify your template name
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        # Check if the entered username and email match a user in the database
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']

        try:
            user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            messages.error(self.request, 'Invalid username or email.')
            return HttpResponseRedirect(self.get_success_url())

        # If the user is found, proceed with sending the password reset email
        form.save(request=self.request)

        # Add your custom logic here if needed

        return super().form_valid(form)
    