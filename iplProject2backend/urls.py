from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("register_user/", views.register_user, name="register_user"),
    path("login_user/", views.login_user, name="login"),
    path("leaderboard1/", views.leaderboard1, name="leaderboard1"),
    path("leaderboard3/", views.leaderboard3, name="leaderboard3"),
    path("fixtures/", views.fixtures, name="fixtures"),
    path('user_input_form', views.user_input_form, name='user_input_form'),
    path('user_submissions/<str:username>/', views.user_submissions, name='user_submissions'),
    path('predict1/<int:match_id>/', views.predict1, name='predict1'),


]
