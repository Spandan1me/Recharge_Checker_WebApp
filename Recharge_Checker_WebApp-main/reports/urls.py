from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('api/get-report/', views.get_report, name='get_report'),
    path('api/save-report/', views.save_report, name='save_report'),

    path('api/get-snapshots/', views.get_snapshots, name='get_snapshots'),
    path('api/get-snapshot/<str:date>/', views.get_snapshot, name='get_snapshot'),
    path('api/save-snapshot/', views.save_snapshot, name='save_snapshot'),
    path('api/clear-snapshots/', views.clear_snapshots, name='clear_snapshots'),
]
