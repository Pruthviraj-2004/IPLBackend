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
from .serializers import MatchInfoSerializer
from django.db.models import Count

@api_view(['GET'])
def home(request):
    # Retrieve all MatchInfo objects
    matches = MatchInfo.objects.all()
    
    # Serialize the queryset
    serializer = MatchInfoSerializer(matches, many=True)
    
    total_users = UserInfo.objects.aggregate(total_users=Count('userID'))['total_users']
    # Return the serialized data as JSON response
    return Response({'matches': serializer.data, 'total_users': total_users})
    
@csrf_exempt
def register_user(request):
    if request.method == "POST":
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

                # Return user data as JSON response
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'name': user_info.name,
                    'email': user.email,
                    # Add any other fields you want to include
                }
                return JsonResponse({'user': user_data}, status=201)  # Status 201 indicates resource creation
            else:
                # If form is not valid, return validation errors as JSON response
                return JsonResponse({'errors': form.errors}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except LbRegistrationTable.DoesNotExist:
            return JsonResponse({'error': 'Leaderboard does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def login_user(request):
    if request.method == "POST":
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
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def logout_user(request):
    logout(request)
    messages.success(request, ("Logged Out Successfully!! "))
    return redirect('home')


def leaderboard1(request):
    # Retrieve all leaderboards
    leaderboards = ['Global', 'Weekly']

    if request.method == 'POST':
        selected_leaderboard = request.POST.get('selected_leaderboard', 'Global')
    else:
        selected_leaderboard = 'Global'

    if selected_leaderboard == 'Global':
        user_list = UserInfo.objects.order_by('-score1', 'username')
    elif selected_leaderboard == 'Weekly':
        user_list = UserInfo.objects.order_by('-score2', 'username')
    else:
        user_list = []

    # Serialize the user_list queryset to JSON format
    serialized_users = serialize('json', user_list)

    # Return the serialized data as a JSON response
    return JsonResponse({
        'leaderboards': leaderboards,
        'selected_leaderboard': selected_leaderboard,
        'user_list': serialized_users
    }, safe=False)

def user_submissions(request, username):
    # Fetch all submissions for the specified user
    user_submissions = SubmissionsInfo5.objects.filter(username=username).order_by('smatch_id')

    # Fetch related match details for each submission
    submission_details = []

    for submission in user_submissions:
        match = MatchInfo.objects.get(matchID=submission.smatch_id)
        submission_details.append({
            'smatchID': submission.smatch_id,
            'predictedteam': submission.predictedteam.teamname,  # Access the team name through ForeignKey relationship
            'predictedpom': submission.predictedpom.playerName if submission.predictedpom else None,  # Check if predictedpom is not None
            'playerofmatch': match.playerofmatch.playerName if match.playerofmatch else None,  # Check if playerofmatch is not None
            'predictedmr': submission.predictedmr.playerName if submission.predictedmr else None,  # Check if predictedmr is not None
            'mostrunsplayer': match.mostrunsplayer.playerName if match.mostrunsplayer else None,  # Check if mostrunsplayer is not None
            'predictedmwk': submission.predictedmwk.playerName if submission.predictedmwk else None,  # Check if predictedmwk is not None
            'mostwickettaker': match.mostwickettaker.playerName if match.mostwickettaker else None,  # Check if mostwickettaker is not None
            'winner_team': match.winner_team.teamname if match.winner_team else None,  # Check if winner_team is not None
            'score': submission.score,
            'match_teamA': match.teamA.teamname,
            'match_teamB': match.teamB.teamname,
            'match_location': match.location,
        })

    # Serialize the data to JSON format
    serialized_data = {
        'username': username,
        'submissions': submission_details,
    }

    # Return the serialized data as a JSON response
    return JsonResponse(serialized_data, safe=False)


from .serializers import MatchInfoSerializer, SubmissionsInfo5Serializer

@api_view(['GET'])
def user_submissions2(request, username):
    # Check if the requested username matches the logged-in user's username
    if request.user.username == username:
        # Fetch all submissions for the specified user
        user_submissions = SubmissionsInfo5.objects.filter(username=username).order_by('smatch_id')
    else:
        # Fetch submissions for the specified username with match status=1
        user_submissions = SubmissionsInfo5.objects.filter(username=username, smatch__status=1).order_by('smatch_id')

    # Serialize submission data
    serialized_submissions = SubmissionsInfo5Serializer(user_submissions, many=True).data

    # Fetch related match details for each submission
    submission_details = []

    for submission in user_submissions:
        match = MatchInfo.objects.get(matchID=submission.smatch_id)
        submission_details.append({
            'smatchID': submission.smatch_id,
            'predictedteam': submission.predictedteam.teamname if submission.predictedteam else None,  # Check if predictedteam is not None
            'predictedpom': submission.predictedpom.playerName if submission.predictedpom else None,  # Check if predictedpom is not None
            'playerofmatch': match.playerofmatch.playerName if match.playerofmatch else None,  # Check if playerofmatch is not None
            'predictedmr': submission.predictedmr.playerName if submission.predictedmr else None,  # Check if predictedmr is not None
            'mostrunsplayer': match.mostrunsplayer.playerName if match.mostrunsplayer else None,  # Check if mostrunsplayer is not None
            'predictedmwk': submission.predictedmwk.playerName if submission.predictedmwk else None,  # Check if predictedmwk is not None
            'mostwickettaker': match.mostwickettaker.playerName if match.mostwickettaker else None,  # Check if mostwickettaker is not None
            'winner_team': match.winner_team.teamname if match.winner_team else None,  # Check if winner_team is not None
            'score': submission.score,
            'match_teamA': match.teamA.teamname,
            'match_teamB': match.teamB.teamname,
            'match_location': match.location,
        })

    # Serialize match details data
    serialized_match_details = submission_details

    # Combine submission and match details
    serialized_data = {
        'username': username,
        'submissions': serialized_submissions,
        'match_details': serialized_match_details,
    }

    # Return the serialized data as a JSON response
    return JsonResponse(serialized_data, safe=False)

class MatchInfoList(APIView):
    def get(self, request):
        # Retrieve all matches with status 0 (upcoming matches) and order them by match date
        match_list = MatchInfo.objects.order_by('matchID', 'matchdate')

        # Serialize the queryset
        serializer = MatchInfoSerializer(match_list, many=True)

        # Return the serialized data as JSON response
        return Response({'match_list': serializer.data})

def leaderboard3(request):
    leaderboards = LbRegistrationTable.objects.all()
    current_user = request.user
    user_participating_leaderboards = []

    # Check if the current user is participating in any leaderboard
    if current_user.is_authenticated:
        user_participating_leaderboards = LbParticipationTable.objects.filter(username__username=current_user.username).values_list('lid__leaderboardname', flat=True)

    # Filter leaderboards based on user's participation
    if user_participating_leaderboards:
        leaderboards = leaderboards.filter(leaderboardname__in=user_participating_leaderboards)
    else:
        # Default to displaying only 'Global' and 'Weekly' leaderboards if the user is not participating
        leaderboards = leaderboards.filter(leaderboardname__in=['Global', 'Weekly'])

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
    return JsonResponse(serialized_data, safe=False)

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

from django.forms.models import model_to_dict
from django.utils import timezone

@csrf_exempt
def predict1(request, match_id):
    if request.method == "POST":
        match = MatchInfo.objects.filter(matchID=match_id).first()
        if not match:
            return JsonResponse({'error': 'Match does not exist'}, status=400)
        if match:
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
                {'name': player.playerName, 'team': 'Team A'} for player in players_A
            ] + [
                {'name': player.playerName, 'team': 'Team B'} for player in players_B
            ]

            # Serialize team_A and team_B
            team_A_data = model_to_dict(team_A)
            team_B_data = model_to_dict(team_B)

            # Filter batsmen and bowlers based on enumeration data type
            batsmen_data = [{'name': player.playerName, 'team': 'Team A'} for player in players_A if player.playerRole in [1, 3, 4]] + [{'name': player.playerName, 'team': 'Team B'} for player in players_B if player.playerRole in [1, 3, 4]]
            bowlers_data = [{'name': player.playerName, 'team': 'Team A'} for player in players_A if player.playerRole in [2, 3]] + [{'name': player.playerName, 'team': 'Team B'} for player in players_B if player.playerRole in [2, 3]]

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



@csrf_exempt
def lb_participation(request):
    if request.method == 'POST':
        # Parse the request body to extract form data
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        print(request.body)
        leaderboardname = body_data.get('leaderboardname')
        password = body_data.get('password')
        username = body_data.get('username')  # Add username to form data
        
        try:
            leaderboard_obj = LbRegistrationTable.objects.get(leaderboardname=leaderboardname)
            if password == leaderboard_obj.password:
                # Fetch the logged-in user's username
                user = UserInfo.objects.get(username=username)
                lb_participation = LbParticipationTable.objects.create(lid=leaderboard_obj, username=user)
                messages.success(request, 'Successfully participated in the leaderboard.')
                return JsonResponse({'success': True})  # Respond with success
            else:
                return JsonResponse({'error': 'Incorrect password'}, status=400)
        except LbRegistrationTable.DoesNotExist:
            return JsonResponse({'error': 'Leaderboard does not exist'}, status=400)
        except UserInfo.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=400)
    
    # Handle other cases or return an error response
    return JsonResponse({'error': 'Invalid request'}, status=400)

def update_match2(request, match_id):
    match_info = MatchInfo.objects.get(pk=match_id)
    form = MatchInfoForm(request.POST or None, instance=match_info)

    if form.is_valid():
        form.save()

        #score_update1(request,match_id)
        #score_update2(request,match_id)
        #revert_score_updates(match_id)
        score_update2(request,match_id)

        messages.success(request, "Match details updated successfully!")
        return redirect('home')

    return render(request, 'ipl2/update_match2.html', {'match_info': match_info, 'form': form})

def score_update2(request, match_id):
    # Fetch the match information
    match = MatchInfo.objects.filter(matchID=match_id).first()##try to add status also
    match_id = int(match_id)

    # If the match exists, proceed with scoring
    if match:
        # Determine the points awarded for correct predictions
        correct_winner_points = 2
        correct_predictions_points = 5

        # Check if it's time to reset score2
        # if match_id % 3 == 0:
        #     reset_weekly(request)  # Call the reset_weekly function

        # Define base points and multipliers
        base_correct_winner_points = 2
        base_correct_predictions_points = 5
        multipliers = [1, 2, 3, 4, 5, 6, 7, 8]

        # Calculate the set number from the match ID
        match_set = match_id % 3

        # Multiply the base points with the multiplier based on the match set
        correct_winner_points = base_correct_winner_points * multipliers[match_set]
        correct_predictions_points = base_correct_predictions_points * multipliers[match_set]

        # Fetch submissions for the specified match and correct predicted team
        submissions = SubmissionsInfo5.objects.filter(smatch_id=match_id, predictedteam=match.winner_team)

        # Update scores for each user who made correct predictions
        for submission in submissions:
            # Fetch the username from the submission
            un = submission.username
            
            # Fetch the user information using the username
            user_info = UserInfo.objects.filter(username=un).first()

            if user_info:
                # Update score1 for correct predicted team
                user_info.score1 += correct_winner_points
                # Update score2 for correct predicted team
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

                # Update score1 for the submission
                submission.score += correct_winner_points

                # Add points for correct predicted team
                if submission.predictedpom == match.playerofmatch:
                    submission.score += correct_predictions_points
                if submission.predictedmr == match.mostrunsplayer:
                    submission.score += correct_predictions_points
                if submission.predictedmwk == match.mostwickettaker:
                    submission.score += correct_predictions_points

                # Save the submission
                submission.save()
