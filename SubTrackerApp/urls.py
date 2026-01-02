from django.contrib import admin
from django.urls import path
from SubTrackerApp import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('add/', views.add_subscription, name='add_subscription'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='home'),
    path('edit/<int:id>/', views.edit_subscription, name='edit_subscription'),
    path('delete/<int:id>/', views.delete_subscription, name='delete_subscription'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
]