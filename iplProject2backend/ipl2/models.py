from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

class TeamInfo(models.Model):
    teamID = models.SmallIntegerField(primary_key=True)
    teamname = models.CharField(max_length=30, null=True)
    teamshortform = models.CharField(max_length=5, null=True)

    def __str__(self):
        return self.teamname

class UserInfo(models.Model):
    userID = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=24, unique=True)
    name = models.CharField(max_length=24)
    email = models.EmailField(unique=True)
    created_on = models.DateTimeField(null=True)#try to make use of user time 
    score1 = models.IntegerField(default=0, null=True)
    score2 = models.IntegerField(default=0, null=True)


    def __str__(self):
        return self.username

class PlayerInfo(models.Model):
    playerID = models.IntegerField(primary_key=True)
    playerName = models.CharField(max_length=24, null=True)
    playerTeamNo = models.ForeignKey(TeamInfo, on_delete=models.CASCADE, null=True, related_name='player_teams')
    playerRole = models.SmallIntegerField(null=True)
    playing11status = models.SmallIntegerField(default=1)


    def __str__(self):
        return self.playerName
    
class MatchInfo(models.Model):
    matchID = models.IntegerField(primary_key=True)
    matchdate = models.DateField(null=True)
    matchtime = models.TimeField(null=True, default='19:30:00')
    teamA = models.ForeignKey(TeamInfo, on_delete=models.CASCADE, null=True, related_name='teamA_matches')
    teamB = models.ForeignKey(TeamInfo, on_delete=models.CASCADE, null=True, related_name='teamB_matches')
    winner_team = models.ForeignKey(TeamInfo, on_delete=models.CASCADE, related_name='winning_matches', blank=True, null=True)

    status = models.SmallIntegerField(default=0)
   
    playerofmatch = models.ForeignKey(PlayerInfo, on_delete=models.CASCADE, related_name='player_of_match', blank=True, null=True)
    mostrunsplayer = models.ForeignKey(PlayerInfo, on_delete=models.CASCADE, related_name='most_runs_player', blank=True, null=True)
    mostwickettaker = models.ForeignKey(PlayerInfo, on_delete=models.CASCADE, related_name='most_wickets_taker', blank=True, null=True)
    
    location = models.CharField(max_length=48, default='Chinnaswamy')

    def __str__(self):
        return f"{self.teamA.teamname} vs {self.teamB.teamname}"
    
class SubmissionsInfo5(models.Model):
    submissionID = models.AutoField(primary_key=True)
    username = models.CharField(max_length=24, null=True)
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, null=True)  # Assuming you have a UserInfo model
    smatch = models.ForeignKey(MatchInfo, on_delete=models.CASCADE)  # ForeignKey to MatchInfo model
    updated_time = models.DateTimeField(null=True)
    predictedteam = models.ForeignKey(TeamInfo, on_delete=models.CASCADE, null=True)  # ForeignKey to TeamInfo model
    predictedpom = models.ForeignKey(PlayerInfo, on_delete=models.CASCADE, null=True, related_name='predicted_pom')  # ForeignKey to PlayerInfo model
    predictedmr = models.ForeignKey(PlayerInfo, on_delete=models.CASCADE, null=True, related_name='predicted_mr')  # ForeignKey to PlayerInfo model
    predictedmwk = models.ForeignKey(PlayerInfo, on_delete=models.CASCADE, null=True, related_name='predicted_mwk')  # ForeignKey to PlayerInfo model
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"Submission ID: {self.submissionID}, Username: {self.username}, Predicted Team: {self.predictedteam}"

class LbRegistrationTable(models.Model):
    lid = models.AutoField(primary_key=True)
    uid = models.ForeignKey(UserInfo, on_delete=models.CASCADE)  # Link to the user who registered the leaderboard
    leaderboardname = models.CharField(max_length=30)
    password = models.CharField(max_length=16)

# Set the table name to lbregistration

    def __str__(self):
        return self.leaderboardname
    
class LbParticipationTable(models.Model):
    lid = models.ForeignKey(LbRegistrationTable, on_delete=models.CASCADE)  # Link to the registered leaderboard
    lpid = models.AutoField(primary_key=True)
    username = models.ForeignKey(UserInfo, on_delete=models.CASCADE, related_name='participations')
    
    
    def __str__(self):
        return f"{self.lid} - {self.username}"


