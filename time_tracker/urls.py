from django.urls import path
from . import views

app_name = 'time_tracker'

urlpatterns = [
    path('', views.task_board, name='board'),
    path('api/tasks/', views.get_tasks, name='get_tasks'),
    path('api/tasks/create/', views.create_task, name='create_task'),
    path('api/tasks/<int:pk>/update/', views.update_task_status, name='update_task'),
    path('api/tasks/<int:pk>/delete/', views.delete_task, name='delete_task'),
]
