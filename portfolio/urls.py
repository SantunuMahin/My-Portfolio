from django.urls import path
from . import views
from .smtpmail import contact_view

app_name = 'portfolio'

urlpatterns = [
    path('', views.index, name='index'),
    path('contact/', contact_view, name='contact'),
    path('search/', views.search_view, name='search'),
    path('test-404/', views.test_404, name='test_404'),
    path('test-403/', views.test_403, name='test_403'),
    path('test-500/', views.test_500, name='test_500'),
]
