"""
Data Access Service - Centralized data management for dashboards
Eliminates session dependency and provides robust data access
"""

import pandas as pd
from pathlib import Path
from django.conf import settings
from typing import Optional, Dict, List, Tuple
from ..models_calculation import CalculationRun, UserDashboardPreference
import logging

logger = logging.getLogger(__name__)


class DataAccessService:
    """
    Centralized service for accessing calculation data across all dashboards
    """
    
    @staticmethod
    def get_user_identifier(request) -> str:
        """Get user identifier (IP for now, can be user ID later)"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'
    
    @staticmethod
    def get_available_runs() -> List[CalculationRun]:
        """Get all available calculation runs"""
        return CalculationRun.objects.filter(
            status__in=['completed', 'updated'],
            is_archived=False
        ).order_by('-created_at')
    
    @staticmethod
    def get_latest_run() -> Optional[CalculationRun]:
        """Get the most recent successful calculation run"""
        return CalculationRun.objects.filter(
            status__in=['completed', 'updated'],
            is_archived=False
        ).first()
    
    @staticmethod
    def get_preferred_run(request) -> Optional[CalculationRun]:
        """Get user's preferred run or latest if no preference"""
        user_id = DataAccessService.get_user_identifier(request)
        
        try:
            prefs = UserDashboardPreference.objects.get(user_identifier=user_id)
            if prefs.preferred_run and prefs.preferred_run.is_data_available:
                return prefs.preferred_run
        except UserDashboardPreference.DoesNotExist:
            pass
        
        # Fallback to latest run
        return DataAccessService.get_latest_run()
    
    @staticmethod
    def set_preferred_run(request, run_id: str) -> bool:
        """Set user's preferred calculation run"""
        user_id = DataAccessService.get_user_identifier(request)
        
        try:
            run = CalculationRun.objects.get(run_id=run_id)
            prefs, created = UserDashboardPreference.objects.get_or_create(
                user_identifier=user_id,
                defaults={'preferred_run': run}
            )
            if not created:
                prefs.preferred_run = run
                prefs.save()
            return True
        except CalculationRun.DoesNotExist:
            return False
    
    @staticmethod
    def load_dashboard_data(run: CalculationRun) -> Dict:
        """
        Load complete dashboard data for a calculation run
        Returns standardized data structure for all dashboards
        """
        if not run or not run.is_data_available:
            return {
                'data_available': False,
                'error': 'No data available'
            }
        
        try:
            # Load parquet files
            result_df = pd.read_parquet(run.get_latest_parquet('result'))
            employee_summary_df = pd.read_parquet(run.get_latest_parquet('employee_summary'))
            adjusted_df = pd.read_parquet(run.get_latest_parquet('adjusted'))
            
            # Prepare project list
            projects_list = sorted(list(result_df['Libelle projet'].unique()))
            
            # Calculate overall KPIs
            overall_kpis = {
                'nbEmployes': int(employee_summary_df['Nom'].nunique()),
                'totalBudgetEstime': float(result_df['Estimees'].sum()),
                'totalAdjustedCost': float(result_df['Adjusted Cost'].sum()),
                'totalEcart': float(result_df['Ecart'].sum()),
                'totalProjects': len(projects_list),
            }
            overall_kpis['pctAjustement'] = (
                (overall_kpis['totalEcart'] / overall_kpis['totalBudgetEstime']) * 100 
                if overall_kpis['totalBudgetEstime'] else 0
            )
            
            # Prepare project-level data
            projects_data = {}
            table_projets = []
            
            for projet_name in projects_list:
                project_result_data = result_df[result_df['Libelle projet'] == projet_name].iloc[0]
                project_employee_data = employee_summary_df[employee_summary_df['Libelle projet'] == projet_name]
                
                # Safe float conversion
                def safe_float(value, default=0.0):
                    if pd.isna(value):
                        return default
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return default
                
                # Project KPIs
                nb_employes_project = project_employee_data['Nom'].nunique()
                budget_estime = safe_float(project_result_data.get('Estimees', 0.0))
                adjusted_cost = safe_float(project_result_data.get('Adjusted Cost', 0.0))
                ecart = safe_float(project_result_data.get('Ecart', 0.0))
                heures_reelles = safe_float(project_result_data.get('Total Heures', 0.0))
                heures_ajustees = safe_float(project_result_data.get('Adjusted Hours', 0.0))
                heures_retirees = safe_float(project_result_data.get('Heures Retirées', 0.0))
                
                pct_ajustement = (ecart / budget_estime) * 100 if budget_estime else 0
                
                # Store in projects_data (for charts/detailed views)
                projects_data[projet_name] = {
                    'kpis': {
                        'nbEmployes': nb_employes_project,
                        'totalBudgetEstime': budget_estime,
                        'totalAdjustedCost': adjusted_cost,
                        'totalEcart': ecart,
                        'pctAjustement': pct_ajustement,
                        'heuresReelles': heures_reelles,
                        'heuresAjustees': heures_ajustees,
                        'heuresRetirees': heures_retirees,
                    },
                    'employee_data': DataAccessService._get_project_employees(adjusted_df, projet_name)
                }
                
                # Calculate Total Cost (Real Hours * Rate) for this project
                project_total_cost = 0.0
                
                if 'Total' in project_employee_data.columns and len(project_employee_data) > 0:
                    total_sum = project_employee_data['Total'].sum()
                    if pd.notna(total_sum) and total_sum > 0:
                        project_total_cost = total_sum
                        logger.debug(f"Project {projet_name}: Using Total column, value = {project_total_cost}")
                    else:
                        logger.debug(f"Project {projet_name}: Total column exists but sum is {total_sum}")
                
                if project_total_cost == 0.0 and 'Rate' in project_employee_data.columns and 'Total Heures' in project_employee_data.columns:
                    # Fallback: calculate manually if Total column is missing, empty, or zero
                    manual_calc = (project_employee_data['Rate'].fillna(0) * project_employee_data['Total Heures'].fillna(0)).sum()
                    if pd.notna(manual_calc) and manual_calc > 0:
                        project_total_cost = manual_calc
                        logger.debug(f"Project {projet_name}: Manual calculation, value = {project_total_cost}")
                    else:
                        logger.debug(f"Project {projet_name}: Manual calculation failed, result = {manual_calc}")
                
                if project_total_cost == 0.0:
                    # Final fallback: use a reasonable estimate based on hours and average rate
                    if heures_reelles > 0:
                        # Estimate rate as adjusted_cost / adjusted_hours if available
                        estimated_rate = adjusted_cost / heures_ajustees if heures_ajustees > 0 else 500  # Default 500€/day
                        project_total_cost = heures_reelles * estimated_rate
                        logger.debug(f"Project {projet_name}: Estimated calculation, value = {project_total_cost} (rate: {estimated_rate})")
                    else:
                        project_total_cost = budget_estime * 0.8  # Estimate 80% of budget
                        logger.debug(f"Project {projet_name}: Budget-based estimate, value = {project_total_cost}")
                
                # Store in table_projets (for table display)
                table_projets.append({
                    'Libelle_projet': projet_name,
                    'Total_Heures': heures_reelles,
                    'Adjusted_Hours': heures_ajustees,
                    'Adjusted_Cost': adjusted_cost,
                    'Heures_Retirees': heures_retirees,
                    'Estimees': budget_estime,
                    'Ecart': ecart,
                    'Total': safe_float(project_total_cost, 0.0),
                })
            
            return {
                'data_available': True,
                'run_info': {
                    'run_id': run.run_id,
                    'period': run.period_string,
                    'created_at': run.created_at,
                    'status': run.status,
                    'has_updates': run.has_updates,
                },
                'overall_kpis': overall_kpis,
                'projects_list': projects_list,
                'projects_data': projects_data,
                'table_projets': table_projets,
                'raw_dataframes': {
                    'result': result_df,
                    'employee_summary': employee_summary_df,
                    'adjusted': adjusted_df,
                } if settings.DEBUG else None  # Only include raw data in debug mode
            }
            
        except Exception as e:
            logger.error(f"Error loading dashboard data for run {run.run_id}: {e}")
            return {
                'data_available': False,
                'error': f'Error loading data: {str(e)}'
            }
    
    @staticmethod
    def _get_project_employees(adjusted_df: pd.DataFrame, projet_name: str) -> List[Dict]:
        """Get employee-level data for a specific project"""
        project_data = adjusted_df[adjusted_df['Libelle projet'] == projet_name]
        
        employees = []
        for _, row in project_data.iterrows():
            employees.append({
                'ID': row.get('ID', ''),
                'Nom': row.get('Nom', ''),
                'Grade': row.get('Grade', ''),
                'Total_Heures': float(row.get('Total Heures', 0.0)),
                'Adjusted_Hours': float(row.get('Adjusted Hours', 0.0)),
                'Rate': float(row.get('Rate', 0.0)),
                'Total_Cost': float(row.get('Total', 0.0)),
                'Adjusted_Cost': float(row.get('Adjusted Cost', 0.0)),
                'Heures_Retirees': float(row.get('Heures Retirées', 0.0)),
            })
        
        return employees
    
    @staticmethod
    def get_dashboard_context(request, run_id: Optional[str] = None) -> Dict:
        """
        Get complete dashboard context for any dashboard
        This is the main method dashboards should use
        """
        # Get the calculation run to use
        if run_id:
            try:
                run = CalculationRun.objects.get(run_id=run_id)
            except CalculationRun.DoesNotExist:
                run = None
        else:
            run = DataAccessService.get_preferred_run(request)
        
        # Load dashboard data
        dashboard_data = DataAccessService.load_dashboard_data(run)
        
        # Add run selection context
        dashboard_data.update({
            'available_runs': DataAccessService.get_available_runs(),
            'current_run': run,
        })
        
        return dashboard_data


class LegacyDataMigration:
    """
    Service to migrate existing parquet files to the new database model
    """
    
    @staticmethod
    def migrate_existing_runs():
        """
        Scan slr_temp_runs directory and create CalculationRun records
        for existing data that doesn't have database entries
        """
        from django.conf import settings
        import re
        from datetime import datetime
        
        runs_dir = Path(settings.MEDIA_ROOT) / 'slr_temp_runs'
        if not runs_dir.exists():
            return []
        
        migrated_runs = []
        existing_run_ids = set(CalculationRun.objects.values_list('run_id', flat=True))
        
        for run_dir in runs_dir.iterdir():
            if not run_dir.is_dir():
                continue
                
            run_id = run_dir.name
            if run_id in existing_run_ids:
                continue  # Already in database
            
            # Check if this directory has data files
            result_file = run_dir / 'result_initial.parquet'
            if not result_file.exists():
                continue
            
            try:
                # Try to extract period information from any available metadata
                period_month = None
                period_year = None
                period_string = "Unknown Period"
                
                # Try to load metadata or infer from creation time
                created_time = datetime.fromtimestamp(run_dir.stat().st_mtime)
                
                # Create the CalculationRun record
                calc_run = CalculationRun.objects.create(
                    run_id=run_id,
                    created_at=created_time,
                    heures_filename="legacy_import",
                    mafe_filename="legacy_import",
                    period_month=period_month,
                    period_year=period_year,
                    period_string=period_string,
                    status='completed',
                    data_directory=f'slr_temp_runs/{run_id}',
                )
                
                # Update summary cache from actual data
                calc_run.update_summary_cache()
                
                migrated_runs.append(calc_run)
                logger.info(f"Migrated legacy run: {run_id}")
                
            except Exception as e:
                logger.error(f"Error migrating run {run_id}: {e}")
        
        return migrated_runs
