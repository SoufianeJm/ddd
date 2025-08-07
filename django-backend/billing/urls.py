from django.urls import path
from . import views
from .views_export import export_all_tables_json
from .views_updated_dashboard import (
    DashboardView, ProjectsDashboardView, EmployeesDashboardView,
    DashboardRessourceView, ApiCalculationDataView, SetPreferredRunView, AvailableRunsView,
    health_check
)
from django.shortcuts import redirect

urlpatterns = [
    path('api/slr/tables/', export_all_tables_json, name='export_all_tables_json'),
    path('', views.facturation_slr, name='home'),
    path('dashboard/', views.dashboard1, name='dashboard'),
    path('dashboard/projects/', lambda request: redirect('/dashboard/', permanent=False), name='dashboard_projects_redirect'),
    path('dashboard/old/', views.dashboard1, name='dashboard_old'),
    path('resources/', views.resource_list_view, name='resource_list'),
    path('dashboard/resources/', DashboardRessourceView.as_view(), name='dashboard_resources'),
    path('resources/create/', views.resource_create, name='resource_create'),
    path('resources/<int:pk>/update/', views.resource_update, name='resource_update'),
    path('resources/<int:pk>/delete/', views.resource_delete, name='resource_delete'),
    path('missions/', views.mission_list_view, name='mission_list'),
    path('missions/create/', views.mission_create, name='mission_create'),
    path('missions/<int:pk>/update/', views.mission_update, name='mission_update'),
    path('missions/<int:pk>/delete/', views.mission_delete, name='mission_delete'),
    path('facturation/slr/', views.facturation_slr, name='facturation_slr'),
    path('missions/bulk-delete/', views.mission_bulk_delete, name='mission_bulk_delete'),
    path('facturation/slr/<str:run_id>/download/<str:filename>/', views.download_slr_report, name='download_slr_report'),
    path('facturation/slr/<str:run_id>/edit/', views.edit_slr_adjustments, name='edit_slr_adjustments'),
    path('facturation/slr/ajax/update-adjusted-hours/', views.ajax_update_adjusted_hours, name='ajax_update_adjusted_hours'),
    path('facturation/slr/<str:run_id>/ajax/project-dates/', views.ajax_get_project_dates, name='ajax_get_project_dates'),
    path('facturation/slr/<str:run_id>/download-ibm/', views.download_ibm_report, name='download_ibm_report'),
    
    # API endpoints for calculation data management (keeping these for potential future use)
    path('api/calculation-data/', ApiCalculationDataView.as_view(), name='api_calculation_data'),
    path('api/set-preferred-run/', SetPreferredRunView.as_view(), name='api_set_preferred_run'),
    path('api/available-runs/', AvailableRunsView.as_view(), name='api_available_runs'),
    path('api/health-check/', health_check, name='api_health_check'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
]
