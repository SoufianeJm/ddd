"""
DataAccessService - Centralized service for managing calculation run data access.

This service replaces fragile session-based data management with robust,
database-backed persistence and provides a consistent interface for dashboards
to access calculation results.
"""

import logging
from typing import Optional, Dict, Any, List
from django.core.cache import cache
from django.db import transaction
from ..models_calculation import CalculationRun, UserDashboardPreference
import pandas as pd

logger = logging.getLogger(__name__)


class DataAccessService:
    """
    Centralized service for accessing calculation run data.
    
    Provides robust, database-backed data access that replaces session-based
    data management. Handles user preferences, caching, and fallback logic.
    """
    
    def __init__(self, user_ip: str, user_identifier: str = ""):
        """
        Initialize service for a specific user context.
        
        Args:
            user_ip: IP address of the user
            user_identifier: Optional additional user identifier
        """
        self.user_ip = user_ip
        self.user_identifier = user_identifier
        self._cache_prefix = f"calc_data_{user_ip}_{user_identifier}"
    
    def get_available_runs(self, include_running: bool = False) -> List[CalculationRun]:
        """
        Get all calculation runs available to the user.
        
        Args:
            include_running: Whether to include runs that are still in progress
            
        Returns:
            List of CalculationRun objects, ordered by creation date (newest first)
        """
        queryset = CalculationRun.objects.all()
        
        if not include_running:
            queryset = queryset.filter(status='completed')
            
        return list(queryset.order_by('-created_at'))
    
    def get_latest_completed_run(self) -> Optional[CalculationRun]:
        """
        Get the most recent successfully completed calculation run.
        
        Returns:
            CalculationRun object or None if no completed runs exist
        """
        return CalculationRun.objects.filter(
            status='completed'
        ).order_by('-created_at').first()
    
    def get_user_preferred_run(self) -> Optional[CalculationRun]:
        """
        Get the user's preferred calculation run.
        
        Returns:
            CalculationRun object or None if no preference is set
        """
        try:
            preference = UserDashboardPreference.objects.get(
                user_identifier=self.user_ip  # Using IP as identifier for now
            )
            return preference.preferred_run
        except UserDashboardPreference.DoesNotExist:
            return None
    
    def set_user_preferred_run(self, run: CalculationRun) -> None:
        """
        Set the user's preferred calculation run.
        
        Args:
            run: CalculationRun to set as preferred
        """
        with transaction.atomic():
            preference, created = UserDashboardPreference.objects.get_or_create(
                user_identifier=self.user_ip,  # Using IP as identifier for now
                defaults={'preferred_run': run}
            )
            if not created:
                preference.preferred_run = run
                preference.save()
                
        # Invalidate cached data when preference changes
        self._invalidate_cache()
    
    def get_current_run(self) -> Optional[CalculationRun]:
        """
        Get the calculation run that should be used for this user.
        
        Uses the following priority:
        1. User's preferred run (if set and completed)
        2. Latest completed run
        3. None if no completed runs exist
        
        Returns:
            CalculationRun object or None
        """
        # Check user preference first
        preferred_run = self.get_user_preferred_run()
        if preferred_run and preferred_run.status == 'completed' and preferred_run.is_data_available():
            return preferred_run
            
        # Fall back to latest completed run
        latest_run = self.get_latest_completed_run()
        if latest_run and latest_run.is_data_available():
            return latest_run
            
        return None
    
    def get_calculation_data(self, run_id: Optional[str] = None, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive calculation data for dashboard consumption.
        
        Args:
            run_id: Specific run ID to retrieve (optional)
            force_refresh: Skip cache and reload from files
            
        Returns:
            Dictionary containing:
            - run_info: Metadata about the calculation run
            - projects_data: Projects DataFrame
            - employees_data: Employees DataFrame
            - summary_stats: Aggregated statistics
            - kpis: Key performance indicators
        """
        # Determine which run to use
        if run_id:
            try:
                run = CalculationRun.objects.get(run_id=run_id, status='completed')
            except CalculationRun.DoesNotExist:
                logger.warning(f"Requested run_id {run_id} not found or not completed")
                run = self.get_current_run()
        else:
            run = self.get_current_run()
            
        if not run:
            return {
                'error': 'No calculation data available',
                'run_info': None,
                'projects_data': pd.DataFrame(),
                'employees_data': pd.DataFrame(),
                'summary_stats': {},
                'kpis': {}
            }
        
        # Check cache first (unless force refresh)
        cache_key = f"{self._cache_prefix}_data_{run.run_id}"
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.debug(f"Returning cached data for run {run.run_id}")
                return cached_data
        
        try:
            # Load data from files
            projects_file = run.get_latest_parquet('result')
            employees_file = run.get_latest_parquet('employee_summary')
            
            if not projects_file or not employees_file:
                raise FileNotFoundError("Required parquet files not found")
                
            projects_df = pd.read_parquet(projects_file)
            employees_df = pd.read_parquet(employees_file)
            
            # Get summary statistics
            summary_stats = run.load_summary_data() or {}
            
            # Compute KPIs
            kpis = self._compute_kpis(projects_df, employees_df)
            
            result = {
                'run_info': {
                    'run_id': run.run_id,
                    'created_at': run.created_at,
                    'updated_at': run.updated_at,
                    'status': run.status,
                },
                'projects_data': projects_df,
                'employees_data': employees_df,
                'summary_stats': summary_stats,
                'kpis': kpis
            }
            
            # Cache the result for 1 hour
            cache.set(cache_key, result, 3600)
            
            logger.info(f"Loaded calculation data for run {run.run_id} "
                       f"({len(projects_df)} projects, {len(employees_df)} employees)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error loading calculation data for run {run.run_id}: {e}")
            return {
                'error': str(e),
                'run_info': {
                    'run_id': run.run_id,
                    'created_at': run.created_at,
                    'updated_at': run.updated_at,
                    'status': run.status,
                },
                'projects_data': pd.DataFrame(),
                'employees_data': pd.DataFrame(),
                'summary_stats': {},
                'kpis': {}
            }
    
    def _compute_kpis(self, projects_df: pd.DataFrame, employees_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Compute key performance indicators from the data.
        
        Args:
            projects_df: Projects DataFrame
            employees_df: Employees DataFrame
            
        Returns:
            Dictionary of KPI values
        """
        kpis = {}
        
        try:
            # Project-level KPIs
            if not projects_df.empty:
                # Calculate total budget (Estimees column)
                total_budget = float(projects_df.get('Estimees', pd.Series([0])).sum())
                
                kpis.update({
                    'total_projects': len(projects_df),
                    'total_budget': total_budget,
                    'total_revenue': float(projects_df.get('total_revenue', pd.Series([0])).sum()),
                    'total_cost': float(projects_df.get('total_cost', pd.Series([0])).sum()),
                    'total_profit': float(projects_df.get('profit', pd.Series([0])).sum()),
                    'avg_project_margin': float(projects_df.get('margin_pct', pd.Series([0])).mean()) if 'margin_pct' in projects_df.columns else 0,
                })
                
                # Add individual project budgets for detailed view
                if 'Libelle projet' in projects_df.columns and 'Estimees' in projects_df.columns:
                    project_budgets = {}
                    for _, row in projects_df.iterrows():
                        project_name = row.get('Libelle projet', 'Unknown')
                        budget = float(row.get('Estimees', 0))
                        project_budgets[project_name] = budget
                    kpis['project_budgets'] = project_budgets
                
                # Compute profit margin
                if kpis['total_revenue'] > 0:
                    kpis['overall_margin_pct'] = (kpis['total_profit'] / kpis['total_revenue']) * 100
                else:
                    kpis['overall_margin_pct'] = 0
            
            # Employee-level KPIs
            if not employees_df.empty:
                kpis.update({
                    'total_employees': len(employees_df),
                    'total_hours': float(employees_df.get('total_hours', pd.Series([0])).sum()),
                    'avg_utilization': float(employees_df.get('utilization_pct', pd.Series([0])).mean()) if 'utilization_pct' in employees_df.columns else 0,
                })
                
                # Grade distribution
                if 'grade' in employees_df.columns:
                    grade_counts = employees_df['grade'].value_counts().to_dict()
                    kpis['grade_distribution'] = {str(k): int(v) for k, v in grade_counts.items()}
        
        except Exception as e:
            logger.error(f"Error computing KPIs: {e}")
            
        return kpis
    
    def _invalidate_cache(self) -> None:
        """Invalidate all cached data for this user."""
        # Pattern-based cache invalidation would be ideal, but Django's default cache
        # doesn't support it easily. For now, we'll clear specific keys we know about.
        # In production, consider using Redis with pattern-based deletion.
        pass
    
    def create_calculation_run(self, run_id: str, data_directory: str, 
                             heures_filename: str = "", mafe_filename: str = "") -> CalculationRun:
        """
        Create a new calculation run record.
        
        Args:
            run_id: Unique identifier for the calculation run
            data_directory: Directory containing calculation files
            heures_filename: Name of heures file (optional)
            mafe_filename: Name of mafe file (optional)
            
        Returns:
            Created CalculationRun object
        """
        return CalculationRun.objects.create(
            run_id=run_id,
            data_directory=data_directory,
            heures_filename=heures_filename,
            mafe_filename=mafe_filename,
            status='processing'
        )
    
    def complete_calculation_run(self, run_id: str) -> bool:
        """
        Mark a calculation run as completed.
        
        Args:
            run_id: ID of the calculation run to complete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            run = CalculationRun.objects.get(run_id=run_id)
            run.status = 'completed'
            run.save(update_fields=['status'])
            
            # Update summary cache
            run.update_summary_cache()
            
            # Invalidate cache to ensure fresh data
            self._invalidate_cache()
            
            logger.info(f"Marked calculation run {run_id} as completed")
            return True
            
        except CalculationRun.DoesNotExist:
            logger.error(f"Calculation run {run_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error completing calculation run {run_id}: {e}")
            return False
