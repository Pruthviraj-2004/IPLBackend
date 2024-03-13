from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import MatchInfoList, UserSubmissions, LBParticipationView, RegisterUserView, LoginUserView
from django.views.decorators.csrf import csrf_exempt
from .views import CustomPasswordResetView

urlpatterns = [
    path("home/", views.home, name="home"),
    path("register_user/", views.RegisterUserView.as_view(), name="register_user"),
    path("login_user/", views.LoginUserView.as_view(), name="login"),
    path("logout_user/", views.logout_user, name="logout"),
    path("leaderboard2/", views.leaderboard2, name="leaderboard2"),
    path('fixtures/', views.MatchInfoList.as_view(), name='fixtures'),
    path('user_submissions/<str:username>/', views.UserSubmissions.as_view(), name='user_submissions'),
    path('predict1/<int:match_id>/', views.predict1, name='predict1'),
    path('lb_participation/', views.LBParticipationView.as_view(), name='lb_participation'),
    path("update_match2/<match_id>", views.update_match2, name="update_match2"),


    path("lb_registration", views.lb_registration, name="lb_registration"),
    path('suggest_password/', views.suggest_password, name='suggest_password'),
    path('control-panel', views.control_panel, name='control_panel'),

    # path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',views.activate, name='activate'),
    path('password_reset/', CustomPasswordResetView.as_view(template_name='ipl2/password_reset_form.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='ipl2/password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='ipl2/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='ipl2/password_reset_complete.html'), name='password_reset_complete'),

]
