from django.urls import path
from . import views

app_name = 'pin_interast'

urlpatterns = [
    path('', views.board_list, name='board_list'),
    path('all/', views.all_pins, name='all_pins'),
    path('import/', views.pinterest_import, name='import'),
    path('register/', views.pinterest_register, name='register'),
    path('music/api/', views.api_music_tracks, name='api_music_tracks'),
    path('music/api/add/', views.api_add_music_track, name='api_add_music_track'),
    path('music/api/<int:track_id>/favorite/', views.api_toggle_favorite, name='api_toggle_favorite'),
    path('music/api/<int:track_id>/delete/', views.api_delete_music_track, name='api_delete_music_track'),
    path('<slug:slug>/', views.board_detail, name='board_detail'),
    path('<slug:board_slug>/<int:pk>/', views.pin_detail, name='pin_detail'),
]

