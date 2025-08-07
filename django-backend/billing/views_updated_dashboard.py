"""
Updated dashboard views using the DataAccessService for robust data management.

These views replace session-based data access with the new database-backed
persistence system, providing reliable access to calculation results.
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse
import json
import logging

from .services.data_access_service import DataAccessService
from .models_calculation import CalculationRun

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class DashboardView(View):
    """
    Main dashboard view using DataAccessService for robust data access.
    """
    
    def get(self, request):
        """Render the main dashboard with calculation data."""
        user_ip = get_client_ip(request)
        data_service = DataAccessService(user_ip=user_ip)
        
        # Get calculation data
        calc_data = data_service.get_calculation_data()
        
        # Get available runs for the dropdown
        available_runs = data_service.get_available_runs()
        current_run = data_service.get_current_run()
        
        context = {
            'calculation_data': calc_data,
            'available_runs': available_runs,
            'current_run': current_run,
            'has_data': not calc_data.get('error'),
            'error_message': calc_data.get('error'),
        }
        
        if calc_data.get('error'):
            messages.error(request, f"No calculation data available: {calc_data['error']}")
        
        return render(request, 'billing/dashboard_enhanced.html', context)


class ProjectsDashboardView(View):
    """Projects-specific dashboard view."""
    
    def get(self, request):
        user_ip = get_client_ip(request)
        data_service = DataAccessService(user_ip=user_ip)
        
        # Get specific run if requested
        run_id = request.GET.get('run_id')
        calc_data = data_service.get_calculation_data(run_id=run_id)
        
        if calc_data.get('error'):
            messages.error(request, f"Could not load projects data: {calc_data['error']}")
            return redirect('dashboard')
        
        # Prepare projects data for the template
        projects_df = calc_data['projects_data']
        projects_data = []
        
        if not projects_df.empty:
            # Convert DataFrame to list of dictionaries for template rendering
            projects_data = projects_df.to_dict('records')
            
            # Format currency fields
            for project in projects_data:
                for field in ['total_revenue', 'total_cost', 'profit']:
                    if field in project and project[field] is not None:
                        project[f'{field}_formatted'] = f"€{project[field]:,.2f}"
                
                # Format percentage fields
                if 'margin_pct' in project and project['margin_pct'] is not None:
                    project['margin_pct_formatted'] = f"{project['margin_pct']:.1f}%"
        
        context = {
            'projects_data': projects_data,
            'run_info': calc_data['run_info'],
            'summary_stats': calc_data['summary_stats'],
            'kpis': calc_data['kpis'],
            'available_runs': data_service.get_available_runs(),
        }
        
        return render(request, 'billing/projects_dashboard.html', context)


class DashboardRessourceView(View):
    """Resource-specific dashboard view with SLR visualization data."""
    
    def get(self, request):
        import json
        from pathlib import Path
        from django.conf import settings
        import pandas as pd
        from billing.views import TEMP_FILES_BASE_DIR
        
        def get_latest_parquet(run_dir, base):
            updated = run_dir / f'{base}_updated.parquet'
            initial = run_dir / f'{base}_initial.parquet'
            return updated if updated.exists() else initial

        last_slr_run_id = request.session.get('last_slr_run_id')
        
        # FALLBACK: If no session run_id, try to find the most recent run
        if not last_slr_run_id:
            try:
                runs_dir = TEMP_FILES_BASE_DIR
                if runs_dir.exists():
                    run_dirs = [d for d in runs_dir.iterdir() if d.is_dir()]
                    if run_dirs:
                        most_recent_run = max(run_dirs, key=lambda x: x.stat().st_mtime)
                        last_slr_run_id = most_recent_run.name
                        request.session['last_slr_run_id'] = last_slr_run_id
            except Exception as e:
                print(f"DEBUG: Error finding fallback run_id: {e}")
        
        data_available = False
        unique_employees = []
        adjusted_data = []
        employee_summary_data = []
        global_summary_data = []
        overall_kpis = {}
        
        if last_slr_run_id:
            run_dir = TEMP_FILES_BASE_DIR / last_slr_run_id
            try:
                # Load the necessary DataFrames
                adjusted_df = pd.read_parquet(run_dir / 'adjusted_initial.parquet')
                employee_summary = pd.read_parquet(run_dir / 'employee_summary_initial.parquet')
                global_summary = pd.read_parquet(run_dir / 'global_summary_initial.parquet')
                result_df = pd.read_parquet(run_dir / 'result_initial.parquet')
                
                data_available = True
                
                # Get unique employees (ensure no duplicates)
                unique_employees = sorted(set(adjusted_df['Nom'].unique()))
                
                # Prepare data for charts and tables
                for _, row in adjusted_df.iterrows():
                    adjusted_data.append({
                        'Nom': row['Nom'],
                        'Libelle_projet': row['Libelle projet'],
                        'Total_Heures': float(row['Total Heures']),
                        'Adjusted_Hours': float(row['Adjusted Hours']),
                        'Heures_Retirées': float(row['Heures Retirées']),
                        'final_coeff': float(row.get('final_coeff', 0))
                    })

                for _, row in employee_summary.iterrows():
                    employee_summary_data.append({
                        'Nom': row['Nom'],
                        'Libelle_projet': row['Libelle projet'],
                        'Total_Heures': float(row['Total Heures']),
                        'Total': float(row['Total']),
                        'Total_DES': float(row['Total DES'])
                    })

                for _, row in global_summary.iterrows():
                    total_heures = float(row['Total Heures'])
                    estimees = float(row['Estimees'])
                    
                    # Skip projects where both estimees and Total_Heures are 0
                    if estimees == 0 and total_heures == 0:
                        continue
                        
                    global_summary_data.append({
                        'Libelle_projet': row['Libelle projet'],
                        'Total_Heures': total_heures,
                        'Total': float(row['Total']),
                        'Total_DES': float(row['Total DES']),
                        'Estimees': estimees
                    })
                
                # Calculate decision-focused KPIs for managers
                total_budget_estime_overall = result_df['Estimees'].sum()
                total_adjusted_cost_overall = result_df['Adjusted Cost'].sum()
                total_ecart_overall = result_df['Ecart'].sum()
                
                # Calculate KPIs matching the template structure
                # 1. Total Budget (Budget Total Estimés) - ligne 37 du template
                totalBudget = total_budget_estime_overall
                
                # 2. Max Hours to Remove - Calculate based on overrun
                total_hours = adjusted_df['Total Heures'].sum()
                total_hours_removed = adjusted_df['Heures Retirées'].sum()
                max_hours_to_remove = total_hours_removed
                
                # 3. Project to Remove From - Find project with highest overrun
                remove_from_project = "N/A"
                if len(result_df[result_df['Ecart'] < 0]) > 0:
                    worst_project = result_df.loc[result_df['Ecart'].idxmin()]
                    remove_from_project = worst_project['Libelle projet']
                
                # 4. Mission Budget - Same as total budget for now
                mission_budget = total_budget_estime_overall
                
                # 5. Potential Savings (Économies Estimées)
                # Calculate savings from adjustments
                original_cost = result_df['Total Heures'].sum() * (total_adjusted_cost_overall / total_hours if total_hours > 0 else 0)
                potential_savings = original_cost - total_adjusted_cost_overall
                
                # 6. Employee Impact - Number of unique employees
                employee_count = len(unique_employees)
                
                overall_kpis = {
                    'totalBudget': totalBudget,
                    'maxHoursToRemove': max_hours_to_remove,
                    'removeFromProject': remove_from_project,
                    'missionBudget': mission_budget,
                    'potentialSavings': potential_savings,
                    'employeeImpact': employee_count,
                    # Keep old values for compatibility
                    'projetsDepassantBudget': len(result_df[result_df['Ecart'] < 0]),
                    'projetsSousBudget': len(result_df[result_df['Ecart'] > 0]),
                    'montantDepassement': abs(result_df[result_df['Ecart'] < 0]['Ecart'].sum()),
                    'economiesPotentielles': potential_savings,
                    'coutMoyenHeure': total_adjusted_cost_overall / total_hours if total_hours > 0 else 0,
                    'projetsUrgents': len(result_df[(result_df['Ecart'] < 0) & (abs(result_df['Ecart'] / result_df['Estimees']) > 0.20)]),
                    'totalProjets': len(result_df),
                    'pourcentageDepassement': (len(result_df[result_df['Ecart'] < 0]) / len(result_df) * 100) if len(result_df) > 0 else 0
                }
                
            except Exception as e:
                print(f"ERROR: Failed to load SLR data: {e}")
                data_available = False
        
        # Add download and adjust URLs if data is available
        download_url = None
        adjust_url = None
        initial_excel_filename = None
        
        if data_available and last_slr_run_id:
            # Look for available Excel files in the run directory
            run_dir = TEMP_FILES_BASE_DIR / last_slr_run_id
            try:
                # Find the initial Excel file
                excel_files = list(run_dir.glob('Initial_SLR_Report_*.xlsx'))
                if excel_files:
                    initial_excel_filename = excel_files[0].name
                    download_url = reverse('download_slr_report', args=[last_slr_run_id, initial_excel_filename])
                
                # Always provide adjust URL if run exists
                adjust_url = reverse('edit_slr_adjustments', args=[last_slr_run_id])
            except Exception as e:
                print(f"DEBUG: Error generating URLs: {e}")
        
        # Prepare context
        context = {
            'page_title': 'SLR Data Visualization - Resource Dashboard',
            'run_id': last_slr_run_id,
            'data_available': data_available,
            'unique_employees': unique_employees,
            'adjusted_data_json': json.dumps(adjusted_data),
            'employee_summary_json': json.dumps(employee_summary_data),
            'global_summary_json': json.dumps(global_summary_data),
            'adjusted_data': adjusted_data,
            'employee_summary': employee_summary_data,
            'global_summary': global_summary_data,
            'overall_kpis': overall_kpis,
            'download_url': download_url,
            'adjust_url': adjust_url,
            'initial_excel_filename': initial_excel_filename,
        }
        
        return render(request, 'billing/dashboard_ressource.html', context)

class EmployeesDashboardView(View):
    """Employees-specific dashboard view."""
    
    def get(self, request):
        user_ip = get_client_ip(request)
        data_service = DataAccessService(user_ip=user_ip)
        
        # Get specific run if requested
        run_id = request.GET.get('run_id')
        calc_data = data_service.get_calculation_data(run_id=run_id)
        
        if calc_data.get('error'):
            messages.error(request, f"Could not load employees data: {calc_data['error']}")
            return redirect('dashboard')
        
        # Prepare employees data for the template
        employees_df = calc_data['employees_data']
        employees_data = []
        
        if not employees_df.empty:
            employees_data = employees_df.to_dict('records')
            
            # Format currency and percentage fields
            for employee in employees_data:
                for field in ['total_revenue', 'total_cost']:
                    if field in employee and employee[field] is not None:
                        employee[f'{field}_formatted'] = f"€{employee[field]:,.2f}"
                
                if 'utilization_pct' in employee and employee['utilization_pct'] is not None:
                    employee['utilization_pct_formatted'] = f"{employee['utilization_pct']:.1f}%"
        
        context = {
            'employees_data': employees_data,
            'run_info': calc_data['run_info'],
            'summary_stats': calc_data['summary_stats'],
            'kpis': calc_data['kpis'],
            'available_runs': data_service.get_available_runs(),
        }
        
        return render(request, 'billing/employees_dashboard.html', context)


class ApiCalculationDataView(View):
    """API endpoint for retrieving calculation data as JSON."""
    
    def get(self, request):
        user_ip = get_client_ip(request)
        data_service = DataAccessService(user_ip=user_ip)
        
        run_id = request.GET.get('run_id')
        force_refresh = request.GET.get('force_refresh') == 'true'
        
        calc_data = data_service.get_calculation_data(
            run_id=run_id, 
            force_refresh=force_refresh
        )
        
        # Convert DataFrames to JSON-serializable format
        response_data = {
            'run_info': calc_data['run_info'],
            'summary_stats': calc_data['summary_stats'],
            'kpis': calc_data['kpis'],
            'error': calc_data.get('error'),
        }
        
        # Convert DataFrames to records if they exist
        if not calc_data['projects_data'].empty:
            response_data['projects'] = calc_data['projects_data'].to_dict('records')
        else:
            response_data['projects'] = []
            
        if not calc_data['employees_data'].empty:
            response_data['employees'] = calc_data['employees_data'].to_dict('records')
        else:
            response_data['employees'] = []
        
        return JsonResponse(response_data)


class SetPreferredRunView(View):
    """API endpoint for setting user's preferred calculation run."""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            run_id = data.get('run_id')
            
            if not run_id:
                return JsonResponse({'error': 'run_id is required'}, status=400)
            
            # Verify the run exists and is completed
            try:
                run = CalculationRun.objects.get(run_id=run_id, status='completed')
            except CalculationRun.DoesNotExist:
                return JsonResponse({'error': 'Invalid or incomplete run_id'}, status=404)
            
            # Set user preference
            user_ip = get_client_ip(request)
            data_service = DataAccessService(user_ip=user_ip)
            data_service.set_user_preferred_run(run)
            
            return JsonResponse({
                'success': True,
                'message': f'Preferred run set to {run_id}'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error setting preferred run: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


class AvailableRunsView(View):
    """API endpoint for listing available calculation runs."""
    
    def get(self, request):
        user_ip = get_client_ip(request)
        data_service = DataAccessService(user_ip=user_ip)
        
        available_runs = data_service.get_available_runs()
        current_run = data_service.get_current_run()
        
        runs_data = []
        for run in available_runs:
            runs_data.append({
                'run_id': run.run_id,
                'created_at': run.created_at.isoformat(),
                'updated_at': run.updated_at.isoformat() if run.updated_at else None,
                'status': run.status,
                'summary_stats': run.summary_stats,
                'is_current': current_run and run.run_id == current_run.run_id,
            })
        
        return JsonResponse({
            'runs': runs_data,
            'current_run_id': current_run.run_id if current_run else None,
        })


# Utility views for backwards compatibility and testing

def dashboard_legacy_redirect(request):
    """Redirect legacy dashboard URLs to new views."""
    messages.info(request, "Dashboard has been updated with improved data management.")
    return redirect('dashboard')


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint to verify data access service."""
    try:
        user_ip = get_client_ip(request)
        data_service = DataAccessService(user_ip=user_ip)
        available_runs = data_service.get_available_runs()
        
        return JsonResponse({
            'status': 'healthy',
            'available_runs': len(available_runs),
            'service': 'DataAccessService',
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
        }, status=500)
