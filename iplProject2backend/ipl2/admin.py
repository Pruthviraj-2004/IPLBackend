from django.contrib import admin

from .models import TeamInfo, UserInfo, PlayerInfo, MatchInfo, SubmissionsInfo5

class TeamInfoAdmin(admin.ModelAdmin):
    list_display = ('teamID', 'teamname', 'teamshortform')
    search_fields = ('teamname', 'teamshortform')

class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('userID', 'username', 'name', 'email', 'created_on', 'score1', 'score2')
    search_fields = ('username', 'email')
    list_filter = ('created_on',)

class PlayerInfoAdmin(admin.ModelAdmin):
    list_display = ('playerID', 'playerName', 'get_teamname', 'playerRole', 'playing11status')
    search_fields = ('playerName',)
    list_filter = ('playerTeamNo__teamname', 'playing11status')  # Use 'playerTeamNo__teamname' to filter by team name

    def get_teamname(self, obj):
        return obj.playerTeamNo.teamname if obj.playerTeamNo else ''  # Check if playerTeamNo is not None
    get_teamname.admin_order_field = 'playerTeamNo__teamname'  # Allows column order sorting based on team name
    get_teamname.short_description = 'Team Name'  # Renames column head

admin.site.register(TeamInfo, TeamInfoAdmin)
admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(PlayerInfo, PlayerInfoAdmin)

class SubmissionsInfoAdmin(admin.ModelAdmin):
    list_display = ('submissionID', 'username', 'user', 'smatch', 'updated_time', 'predictedteam', 'predictedpom', 'predictedmr', 'predictedmwk', 'score')
    list_filter = ('updated_time', 'predictedteam')
    search_fields = ('submissionID', 'username')

admin.site.register(SubmissionsInfo5, SubmissionsInfoAdmin)

from .models import LbRegistrationTable

@admin.register(LbRegistrationTable)
class LbRegistrationTableAdmin(admin.ModelAdmin):
    list_display = ('lid', 'uid', 'leaderboardname','password')
    search_fields = ('leaderboardname',)


from .models import LbParticipationTable

@admin.register(LbParticipationTable)
class LbParticipationTableAdmin(admin.ModelAdmin):
    list_display = ('lpid', 'lid', 'username')
    list_filter = ('lid', 'username')
    #search_fields = ('lid__leaderboardname', 'username__username')


class MatchInfo5Admin(admin.ModelAdmin):
    list_display = ('matchID', 'matchdate', 'matchtime', 'teamA', 'teamB', 'winner_team', 'status')
    list_filter = ('matchdate', 'status')
    search_fields = ('matchID', 'teamA__teamname', 'teamB__teamname')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "winner_team":
            match_id = request.resolver_match.kwargs.get('object_id')
            if match_id:
                try:
                    # Get the match object
                    match = MatchInfo.objects.get(matchID=match_id)
                    # Create queryset with the teams involved in the match
                    team_ids = [match.teamA_id, match.teamB_id]
                    kwargs["queryset"] = TeamInfo.objects.filter(teamID__in=team_ids)
                except MatchInfo.DoesNotExist:
                    pass
        elif db_field.name in ["playerofmatch", "mostrunsplayer", "mostwickettaker"]:
            match_id = request.resolver_match.kwargs.get('object_id')
            if match_id:
                try:
                    # Get the match object
                    match = MatchInfo.objects.get(matchID=match_id)
                    # Get the team IDs for filtering playerofmatch, mostrunsplayer, mostwickettaker
                    team_ids = [match.teamA_id, match.teamB_id]
                    # Filter the respective queryset based on team IDs and playing11status
                    if db_field.name == "mostrunsplayer":
                        kwargs["queryset"] = PlayerInfo.objects.filter(playerTeamNo__in=team_ids, playing11status=1, playerRole__in=[1, 3, 4])
                    elif db_field.name == "mostwickettaker":
                        kwargs["queryset"] = PlayerInfo.objects.filter(playerTeamNo__in=team_ids, playing11status=1, playerRole__in=[2, 3])
                    else:
                        kwargs["queryset"] = PlayerInfo.objects.filter(playerTeamNo__in=team_ids, playing11status=1)
                except MatchInfo.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(MatchInfo, MatchInfo5Admin)
