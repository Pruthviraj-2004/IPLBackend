from rest_framework import serializers
from .models import TeamInfo, UserInfo, PlayerInfo, MatchInfo, SubmissionsInfo5, LbRegistrationTable, LbParticipationTable

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
    predictedteam = serializers.SerializerMethodField()
    predictedpom = serializers.SerializerMethodField()
    predictedmr = serializers.SerializerMethodField()
    predictedmwk = serializers.SerializerMethodField()
    match_teamA = serializers.SerializerMethodField()
    match_teamB = serializers.SerializerMethodField()
    playerofmatch = serializers.SerializerMethodField()
    mostrunsplayer = serializers.SerializerMethodField()
    mostwickettaker = serializers.SerializerMethodField()
    winner_team = serializers.SerializerMethodField()

    class Meta:
        model = SubmissionsInfo5
        fields = ['submissionID', 'username', 'score', 'smatch_id', 'predictedteam', 'predictedpom', 'predictedmr', 'predictedmwk',
                  'match_teamA', 'match_teamB', 'playerofmatch', 'mostrunsplayer', 'mostwickettaker', 'winner_team']

    def get_predictedteam(self, obj):
        return obj.predictedteam.teamname if obj.predictedteam else None

    def get_predictedpom(self, obj):
        return obj.predictedpom.playerName if obj.predictedpom else None

    def get_predictedmr(self, obj):
        return obj.predictedmr.playerName if obj.predictedmr else None

    def get_predictedmwk(self, obj):
        return obj.predictedmwk.playerName if obj.predictedmwk else None

    def get_match_teamA(self, obj):
        return obj.smatch.teamA.teamname if obj.smatch.teamA else None

    def get_match_teamB(self, obj):
        return obj.smatch.teamB.teamname if obj.smatch.teamB else None

    def get_playerofmatch(self, obj):
        return obj.smatch.playerofmatch.playerName if obj.smatch.playerofmatch else None

    def get_mostrunsplayer(self, obj):
        return obj.smatch.mostrunsplayer.playerName if obj.smatch.mostrunsplayer else None

    def get_mostwickettaker(self, obj):
        return obj.smatch.mostwickettaker.playerName if obj.smatch.mostwickettaker else None

    def get_winner_team(self, obj):
        return obj.smatch.winner_team.teamname if obj.smatch.winner_team else None

class LbRegistrationTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = LbRegistrationTable
        fields = '__all__'

class LbParticipationTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = LbParticipationTable
        fields = '__all__'