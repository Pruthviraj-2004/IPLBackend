
from rest_framework import serializers
from .models import TeamInfo, UserInfo, PlayerInfo, MatchInfo, SubmissionsInfo5, LbRegistrationTable, LbParticipationTable

# class TeamInfoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TeamInfo
#         fields = '__all__'

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = '__all__'

class TeamInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamInfo
        fields = ['teamID', 'teamname', 'teamshortform']

class PlayerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerInfo
        fields = ['playerID', 'playerName', 'playerTeamNo', 'playerRole', 'playing11status']

class MatchInfoSerializer(serializers.ModelSerializer):
    teamA = TeamInfoSerializer()
    teamB = TeamInfoSerializer()
    winner_team = TeamInfoSerializer()
    playerofmatch = PlayerInfoSerializer()
    mostrunsplayer = PlayerInfoSerializer()
    mostwickettaker = PlayerInfoSerializer()

    class Meta:
        model = MatchInfo
        fields = ['matchID', 'matchdate', 'matchtime', 'teamA', 'teamB', 'winner_team', 'status', 'playerofmatch', 'mostrunsplayer', 'mostwickettaker', 'location']

class SubmissionsInfo5Serializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionsInfo5
        fields = '__all__'

class LbRegistrationTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = LbRegistrationTable
        fields = '__all__'

class LbParticipationTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = LbParticipationTable
        fields = '__all__'