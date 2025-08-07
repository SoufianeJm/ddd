from django.http import JsonResponse
from .models import Mission

import os
import pandas as pd
from django.conf import settings
from django.http import JsonResponse
from pathlib import Path

def export_all_tables_json(request):
    # Récupère le dernier dossier de run SLR
    last_slr_run_id = request.session.get('last_slr_run_id')
    if not last_slr_run_id:
        return JsonResponse({'error': 'No SLR run found'}, status=404)
    run_dir = Path(settings.MEDIA_ROOT) / 'slr_temp_runs' / last_slr_run_id
    # Définit les chemins des fichiers
    files = {
        'result': run_dir / 'result_updated.parquet',
        'employee_summary': run_dir / 'employee_summary_updated.parquet',
        'global_summary': run_dir / 'global_summary_updated.parquet',
    }
    data = {}
    filtered_projects = set()
    dfs = {}
    # Première passe : lire tous les dfs
    for name, path in files.items():
        if not path.exists():
            path = path.with_name(path.name.replace('_updated', '_initial'))
        if path.exists():
            dfs[name] = pd.read_parquet(path)
        else:
            dfs[name] = pd.DataFrame()
    # Filtrage des projets valides dans result
    if not dfs['result'].empty:
        numeric_cols = dfs['result'].select_dtypes(include=['number']).columns
        filtered_result = dfs['result'][dfs['result'][numeric_cols].abs().sum(axis=1) > 0]
        filtered_projects = set(filtered_result['Libelle projet']) if 'Libelle projet' in filtered_result else set()
        data['result'] = filtered_result.to_dict(orient='records')
    else:
        data['result'] = []
    # Filtrer les autres tables sur les projets valides
    for name in files:
        if name == 'result':
            continue
        df = dfs[name]
        if not df.empty and 'Libelle projet' in df and filtered_projects:
            filtered_df = df[df['Libelle projet'].isin(filtered_projects)]
            data[name] = filtered_df.to_dict(orient='records')
        else:
            data[name] = df.to_dict(orient='records') if not df.empty else []
    return JsonResponse(data, safe=False)
