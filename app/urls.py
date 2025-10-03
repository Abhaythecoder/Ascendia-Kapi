from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('landing/', views.landing, name='landing'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('settings/', views.settings_view, name='settings'),
    path('community/', views.find_creator, name='find_creator'),
    path('profile/<str:username>/', views.creator_profile, name='creator_profile'),
    path('qr-generate/<str:username>/', views.qr_generate_api, name='qr_generate_api'),
    
    path('reset-analytics/', views.reset_analytics, name='reset_analytics'),
]