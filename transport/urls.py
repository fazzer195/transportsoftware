from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
# User Management URLs (Admin only)
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/edit/<int:user_id>/', views.user_edit, name='user_edit'),
    path('users/delete/<int:user_id>/', views.user_delete, name='user_delete'),
    path('users/toggle-status/<int:user_id>/', views.user_toggle_status, name='user_toggle_status'),
    path('get-states/', views.get_states, name='get_states'),
    path('get-cities/', views.get_cities, name='get_cities'),

    # Party URLs
    path('parties/', views.party_list, name='party_list'),
    path('parties/create/', views.party_create, name='party_create'),
    path('parties/edit/<int:party_id>/', views.party_edit, name='party_edit'),
    path('parties/delete/<int:party_id>/', views.party_delete, name='party_delete'),
    path('parties/toggle-status/<int:party_id>/', views.party_toggle_status, name='party_toggle_status'),

    # Truck URLs
    path('trucks/', views.truck_list, name='truck_list'),
    path('trucks/create/', views.truck_create, name='truck_create'),
    path('trucks/edit/<int:truck_id>/', views.truck_edit, name='truck_edit'),
    path('trucks/delete/<int:truck_id>/', views.truck_delete, name='truck_delete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)