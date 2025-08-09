from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/profile/', views.dashboard_profile, name='dashboard_profile'),
    path('dashboard/mixes/', views.dashboard_mixes, name='dashboard_mixes'),
    path('dashboard/featured/', views.dashboard_featured, name='dashboard_featured'),
    path('u/<str:username>/', views.dj_page, name='dj_page'),
    path('mix/<slug:slug>/', views.mix_page, name='mix_page'),
    path('api/mix/<int:mix_id>/played/', views.api_mix_played, name='api_mix_played'),
]
