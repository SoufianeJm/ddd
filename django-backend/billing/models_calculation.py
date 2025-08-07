from django.db import models
from django.utils import timezone
from pathlib import Path
import json

class CalculationRun(models.Model):
    """
    Model to track SLR calculation runs persistently in database
    Replaces fragile session-based approach
    """
    
    # Unique identifier for the run
    run_id = models.CharField(max_length=36, unique=True, db_index=True)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # File information
    heures_filename = models.CharField(max_length=255, default='default_heures.txt')
    mafe_filename = models.CharField(max_length=255, default='default_mafe.txt')
    
    # Extracted period information
    period_month = models.IntegerField(null=True, blank=True)  # 1-12
    period_year = models.IntegerField(null=True, blank=True)   # e.g., 2024
    period_string = models.CharField(max_length=50, blank=True)  # "Janvier 2024"
    
    # Status tracking
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('updated', 'Updated with Adjustments'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    
    # Summary statistics (cached for quick access)
    total_projects = models.IntegerField(default=0)
    total_employees = models.IntegerField(default=0)
    total_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_adjusted_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_variance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # File paths (relative to MEDIA_ROOT)
    data_directory = models.CharField(max_length=500, default='default_directory/')
    
    # Additional metadata as JSON
    metadata = models.JSONField(default=dict, blank=True)
    
    # Error information if failed
    error_message = models.TextField(blank=True)
    
    # User preferences
    is_favorite = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['period_year', 'period_month']),
        ]
    
    def __str__(self):
        return f"Run {self.run_id[:8]} - {self.period_string} ({self.status})"
    
    @property
    def data_path(self):
        """Get the full path to the data directory"""
        from django.conf import settings
        return Path(settings.MEDIA_ROOT) / self.data_directory
    
    @property
    def is_data_available(self):
        """Check if parquet files exist"""
        data_dir = self.data_path
        return (
            data_dir.exists() and
            (data_dir / 'result_initial.parquet').exists() and
            (data_dir / 'employee_summary_initial.parquet').exists()
        )
    
    @property
    def has_updates(self):
        """Check if run has been updated with manual adjustments"""
        data_dir = self.data_path
        return (data_dir / 'result_updated.parquet').exists()
    
    def get_latest_parquet(self, base_name):
        """Get the latest version of a parquet file (updated or initial)"""
        data_dir = self.data_path
        updated_file = data_dir / f'{base_name}_updated.parquet'
        initial_file = data_dir / f'{base_name}_initial.parquet'
        
        if updated_file.exists():
            return updated_file
        elif initial_file.exists():
            return initial_file
        else:
            return None
    
    def load_summary_data(self):
        """Load summary statistics from parquet files"""
        try:
            import pandas as pd
            
            result_file = self.get_latest_parquet('result')
            employee_file = self.get_latest_parquet('employee_summary')
            
            if result_file and employee_file:
                result_df = pd.read_parquet(result_file)
                employee_df = pd.read_parquet(employee_file)
                
                return {
                    'projects': len(result_df),
                    'employees': employee_df['Nom'].nunique(),
                    'budget': float(result_df['Estimees'].sum()),
                    'adjusted_cost': float(result_df['Adjusted Cost'].sum()),
                    'variance': float(result_df['Ecart'].sum()),
                }
        except Exception as e:
            print(f"Error loading summary data for run {self.run_id}: {e}")
        
        return None
    
    def update_summary_cache(self):
        """Update cached summary statistics"""
        summary = self.load_summary_data()
        if summary:
            self.total_projects = summary['projects']
            self.total_employees = summary['employees']
            self.total_budget = summary['budget']
            self.total_adjusted_cost = summary['adjusted_cost']
            self.total_variance = summary['variance']
            self.save(update_fields=[
                'total_projects', 'total_employees', 'total_budget',
                'total_adjusted_cost', 'total_variance'
            ])


class UserDashboardPreference(models.Model):
    """
    Store user dashboard preferences (replaces session storage)
    """
    
    # For now, we'll use IP-based identification
    # In future, this can be linked to User model when authentication is added
    user_identifier = models.CharField(max_length=100, db_index=True)  # IP address or user ID
    
    # Preferred calculation run
    preferred_run = models.ForeignKey(CalculationRun, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Dashboard preferences
    preferred_dashboard = models.CharField(max_length=50, default='dashboard1')  # dashboard1, dashboard2, etc.
    
    # View preferences
    show_archived = models.BooleanField(default=False)
    default_chart_type = models.CharField(max_length=50, default='bar')
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user_identifier']
    
    def __str__(self):
        return f"Preferences for {self.user_identifier}"
