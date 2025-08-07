"""
IBM-specific utility functions for processing Excel workbooks.
"""
import logging

logger = logging.getLogger(__name__)


class ColumnNotFound(Exception):
    """Raised when a required column cannot be found in the workbook."""
    pass


def find_ibm_columns(workbook, sheet_name=0):
    """
    Find IBM-specific columns in an Excel workbook.
    
    Args:
        workbook: openpyxl workbook object
        sheet_name: Sheet name or index (default: 0 for first sheet)
    
    Returns:
        dict: Mapping of column names to column indices
              {'Code projet': col_idx, 'Nom': col_idx, 'Grade': col_idx, 
               'Date de travail': col_idx, 'Heures': col_idx}
    
    Raises:
        ColumnNotFound: If any required column is not found
    """
    # Get the worksheet
    if isinstance(sheet_name, int):
        ws = workbook.worksheets[sheet_name]
    else:
        ws = workbook[sheet_name]
    
    # Read first row and build header map
    header_map = {}
    first_row = ws[1]
    for idx, cell in enumerate(first_row, 1):
        if cell.value:
            header_lower = str(cell.value).lower()
            header_map[header_lower] = idx
    
    # Define search patterns and their corresponding output keys
    search_patterns = {
        'Code projet': ['otp l2'],
        'Nom': ['nom de la ressource'],
        'Grade': ['grade'],
        'Date de travail': ['date de travail'],
        'Heures': ['heures ecf', 'heures']
    }
    
    result = {}
    found_headers = {}  # Track which headers were matched for duplicate detection
    missing_columns = []  # Track missing columns for better error messages
    
    # Search for each required column
    for output_key, patterns in search_patterns.items():
        found_col = None
        matched_header = None
        
        for pattern in patterns:
            pattern_lower = pattern.lower()
            
            # Look for substring matches in headers
            for header_lower, col_idx in header_map.items():
                if pattern_lower in header_lower:
                    if found_col is None:
                        found_col = col_idx
                        matched_header = header_lower
                    else:
                        # Duplicate found - log warning but keep first match
                        logger.warning(
                            f"Multiple columns found for '{output_key}' pattern '{pattern}': "
                            f"'{matched_header}' (column {found_col}) and '{header_lower}' (column {col_idx}). "
                            f"Using first match: '{matched_header}'"
                        )
            
            # If we found a match for this pattern, break and use it
            if found_col is not None:
                break
        
        if found_col is None:
            missing_columns.append(output_key)
        else:
            # Check for ambiguities across different output keys
            if matched_header in found_headers:
                logger.warning(
                    f"Header '{matched_header}' matches multiple output keys: "
                    f"'{found_headers[matched_header]}' and '{output_key}'. "
                    f"Using for '{output_key}'"
                )
            
            found_headers[matched_header] = output_key
            result[output_key] = found_col
    
    # Raise error with detailed information about missing columns
    if missing_columns:
        missing_details = []
        for col in missing_columns:
            patterns = search_patterns[col]
            missing_details.append(f"'{col}' (searched for: {patterns})")
        
        available_headers = list(header_map.keys())
        raise ColumnNotFound(
            f"Required columns not found: {', '.join(missing_details)}. "
            f"Available headers: {available_headers}"
        )
    
    logger.info(f"Successfully mapped IBM columns: {result}")
    return result

def validate_required_columns(workbook, sheet_name=0, required_columns=None):
    """
    Validate that all required columns are present in the Excel workbook.
    
    Args:
        workbook: openpyxl workbook object
        sheet_name: Sheet name or index (default: 0 for first sheet)
        required_columns: List of required column names (default: IBM standard columns)
    
    Returns:
        tuple: (is_valid: bool, missing_columns: list, found_columns: dict)
    
    Raises:
        None - returns status instead of raising exceptions for better error handling
    """
    if required_columns is None:
        required_columns = ['Code projet', 'Nom', 'Grade', 'Date de travail', 'Heures']
    
    try:
        found_columns = find_ibm_columns(workbook, sheet_name)
        # Check if all required columns were found
        missing_columns = [col for col in required_columns if col not in found_columns]
        return len(missing_columns) == 0, missing_columns, found_columns
    except ColumnNotFound as e:
        # Extract missing columns from the error message
        missing_columns = required_columns  # Assume all are missing if detection failed
        return False, missing_columns, {}
