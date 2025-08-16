# --- file: app/urls.py ---
from django.urls import path
from . import views


app_name = 'app'  # Namespace for the app

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('landing/', views.landing, name='landing'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('content/', views.content_management, name='content_management'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('payments/', views.payments, name='payments'),
    path('analytics/', views.analytics, name='analytics'),
    path('profile/<str:username>/', views.creator_profile, name='creator_profile'),

    path('settings/', views.settings_view, name='settings'),

    path('find/', views.find_creator, name='community'),
]
