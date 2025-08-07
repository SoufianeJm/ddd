# Facturation/Billing Management System

A Django-based billing and project management system with both web and desktop deployment capabilities.

## Overview

This application provides comprehensive billing management features including:
- Project calculation and tracking
- Employee billing management
- Dashboard analytics with KPI displays
- Robust data persistence using a database-backed calculation system
- Export capabilities for billing data

## Architecture

The system is built with Django and uses a modern database-backed approach for managing calculation data, replacing fragile session-based systems. Key components include:

- **CalculationRun Model**: Persistent tracking of calculation runs
- **DataAccessService**: Centralized service layer for data access
- **Enhanced Dashboard Views**: Modern class-based views with API endpoints
- **Interactive Templates**: Real-time data refresh and user preferences

## Email/Teams Integration Status

**Important**: This version has **email and Microsoft Teams integrations removed** for simplified deployment and reduced dependencies. The following features have been stripped out:

- Email notifications and alerts
- Microsoft Teams notifications
- OneDrive synchronization (`billing/onedrive_sync.py` removed)
- Mail admin functionality

This creates a standalone version focused on core billing functionality without external communication dependencies.

## Installation

### Prerequisites
- Python 3.13+
- Django and required dependencies (see `requirements.txt`)

### Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run database migrations:
   ```bash
   python manage.py migrate
   ```
4. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

## Running

### Desktop Mode (Recommended)
For standalone desktop usage, simply run:

```bash
python run_desktop.py
```

This single command will:
- Start the Django development server
- Open your default browser to http://127.0.0.1:8000
- Use desktop-optimized settings and logging
- Run in local-only mode without external dependencies

### Development Mode
For development with full Django features:

```bash
python manage.py runserver
```

### Production Deployment
For production environments, configure your web server (Apache/Nginx) to serve the Django application using the standard `slr_project.wsgi` module.

## Key Features

### ✅ Persistent Data Management
- Calculation runs tracked in database
- Data survives server restarts and session timeouts
- Multiple concurrent sessions supported

### ✅ User Preferences
- Users can select preferred calculation runs
- Preferences remembered across sessions
- Automatic fallback to latest available run

### ✅ Robust Error Handling
- Graceful degradation when data unavailable
- Clear error messages and recovery options
- File existence validation

### ✅ Performance & Caching
- Intelligent caching of loaded data
- Summary statistics computed and cached
- Efficient database queries

### ✅ API-First Design
- RESTful endpoints for programmatic access
- JSON data export capabilities
- Real-time run status updates

## API Endpoints

- `GET /api/calculation-data/` - Get calculation data
- `POST /api/set-preferred-run/` - Set user's preferred calculation run
- `GET /api/available-runs/` - List all available calculation runs
- `GET /api/health-check/` - System health status

## Project Structure

```
├── billing/              # Main billing application
├── slr_project/          # Django project settings
├── staticfiles/          # Static assets
├── templates/            # HTML templates
├── run_desktop.py        # Desktop entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Desktop Application

The desktop version includes:
- Simplified setup with `Setup_Facturation.bat`
- One-click launch with `Facturation_Desktop.bat`
- Optimized logging configuration
- Local-only operation mode

## Documentation

For detailed technical documentation about the database-backed calculation system, see `CALCULATION_DATA_SYSTEM.md`.

## Support

For technical support or questions about this billing system, contact your system administrator.

---

**Note**: This is a streamlined version with email/Teams integrations removed for simplified deployment and reduced external dependencies.
