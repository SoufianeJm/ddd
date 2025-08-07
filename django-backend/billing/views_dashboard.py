"""
Modern Dashboard Views using DataAccessService
Session-independent, robust data access for all dashboards
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .services.data_access import DataAccessService
from .models_calculation import CalculationRun
import json


def dashboard_new(request):
    """
    New robust dashboard using DataAccessService
    No session dependency - always finds and displays data
    """
    
    # Get run_id from URL parameter if provided
    run_id = request.GET.get('run_id')
    
    # Get dashboard context using the service
    context = DataAccessService.get_dashboard_context(request, run_id)
    
    # Add template-specific context
    context.update({
        'page_title': 'Analytics Dashboard',
        'dashboard_type': 'new',
        'show_run_selector': True,  # Enable run selection UI
    })
    
    return render(request, 'billing/dashboard_new.html', context)


def dashboard_comparison(request):
    """
    Dashboard for comparing multiple calculation runs
    """
    
    available_runs = DataAccessService.get_available_runs()
    
    # Get selected runs for comparison
    selected_run_ids = request.GET.getlist('runs')
    if not selected_run_ids:
        # Default to latest 2 runs
        selected_run_ids = [run.run_id for run in available_runs[:2]]
    
    comparison_data = []
    for run_id in selected_run_ids:
        try:
            run = CalculationRun.objects.get(run_id=run_id)
            data = DataAccessService.load_dashboard_data(run)
            if data['data_available']:
                comparison_data.append({
                    'run': run,
                    'data': data
                })
        except CalculationRun.DoesNotExist:
            continue
    
    context = {
        'page_title': 'Run Comparison Dashboard',
        'available_runs': available_runs,
        'selected_runs': selected_run_ids,
        'comparison_data': comparison_data,
        'data_available': len(comparison_data) > 0,
    }
    
    return render(request, 'billing/dashboard_comparison.html', context)


def dashboard_project_detail(request, project_name):
    """
    Detailed dashboard for a specific project
    """
    
    # Get the dashboard data
    context = DataAccessService.get_dashboard_context(request)
    
    if not context['data_available']:
        messages.error(request, 'No calculation data available for project details.')
        return redirect('dashboard_new')
    
    # Get project-specific data
    projects_data = context.get('projects_data', {})
    if project_name not in projects_data:
        messages.error(request, f'Project "{project_name}" not found in current calculation.')
        return redirect('dashboard_new')
    
    project_data = projects_data[project_name]
    
    context.update({
        'page_title': f'Project Detail - {project_name}',
        'project_name': project_name,
        'project_data': project_data,
        'employee_data': project_data.get('employee_data', []),
    })
    
    return render(request, 'billing/dashboard_project_detail.html', context)


# API Views for dynamic data access

def api_set_preferred_run(request):
    """
    API endpoint to set user's preferred calculation run
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        run_id = data.get('run_id')
        
        if not run_id:
            return JsonResponse({'error': 'run_id required'}, status=400)
        
        success = DataAccessService.set_preferred_run(request, run_id)
        
        if success:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Invalid run_id'}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_get_run_data(request, run_id):
    """
    API endpoint to get data for a specific calculation run
    """
    try:
        run = CalculationRun.objects.get(run_id=run_id)
        data = DataAccessService.load_dashboard_data(run)
        return JsonResponse(data)
    except CalculationRun.DoesNotExist:
        return JsonResponse({'error': 'Run not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_available_runs(request):
    """
    API endpoint to get list of available calculation runs
    """
    runs = DataAccessService.get_available_runs()
    
    runs_data = []
    for run in runs:
        runs_data.append({
            'run_id': run.run_id,
            'period': run.period_string,
            'created_at': run.created_at.isoformat(),
            'status': run.status,
            'total_projects': run.total_projects,
            'total_employees': run.total_employees,
            'total_budget': float(run.total_budget),
            'has_updates': run.has_updates,
            'is_favorite': run.is_favorite,
        })
    
    return JsonResponse({'runs': runs_data})


def migrate_legacy_data(request):
    """
    Management view to migrate existing parquet files to database
    """
    if request.method == 'POST':
        from .services.data_access import LegacyDataMigration
        
        try:
            migrated_runs = LegacyDataMigration.migrate_existing_runs()
            
            if migrated_runs:
                messages.success(
                    request, 
                    f'Successfully migrated {len(migrated_runs)} calculation runs to database.'
                )
            else:
                messages.info(request, 'No new runs found to migrate.')
                
        except Exception as e:
            messages.error(request, f'Error during migration: {str(e)}')
    
    return redirect('dashboard_new')
