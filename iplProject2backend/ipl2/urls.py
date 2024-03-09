from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import MatchInfoList

urlpatterns = [
    path("home/", views.home, name="home"),
    path("register_user/", views.register_user, name="register_user"),
    path("login_user/", views.login_user, name="login"),
    path("logout_user/", views.logout_user, name="logout"),
    path("leaderboard1/", views.leaderboard1, name="leaderboard1"),
    path("leaderboard2/", views.leaderboard2, name="leaderboard2"),
    path("leaderboard3/", views.leaderboard3, name="leaderboard3"),
    # path("fixtures/", views.fixtures, name="fixtures"),
    path('fixtures/', MatchInfoList.as_view(), name='fixtures'),
    path('user_submissions/<str:username>/', views.user_submissions, name='user_submissions'),
    path('predict1/<int:match_id>/', views.predict1, name='predict1'),
    path('lb_participation/', views.lb_participation, name='lb_participation'),
    path("update_match2/<match_id>", views.update_match2, name="update_match2"),
]
