import hashlib
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from dateutil import parser
import re


def generate_transaction_hash(
    date: datetime, 
    description: str, 
    amount: float, 
    user_id: int
) -> str:
    """
    Generate a unique hash for a transaction to detect duplicates
    """
    hash_string = f"{user_id}_{date.isoformat()}_{description}_{amount}"
    return hashlib.sha256(hash_string.encode()).hexdigest()


def normalize_date(date_str: str) -> datetime:
    """
    Parse various date formats into a standard datetime object
    Handles: DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD, etc.
    """
    try:
        # Use dateutil parser for flexible parsing
        return parser.parse(date_str, dayfirst=False)
    except Exception as e:
        raise ValueError(f"Unable to parse date: {date_str}") from e


def clean_amount(amount_str: Any) -> float:
    """
    Clean and parse amount strings
    Handles: $1,234.56, (1234.56), -1234.56, etc.
    """
    if isinstance(amount_str, (int, float)):
        return float(amount_str)
    
    # Remove currency symbols and whitespace
    cleaned = str(amount_str).strip()
    cleaned = re.sub(r'[$€£,\s]', '', cleaned)
    
    # Handle parentheses as negative (accounting format)
    if cleaned.startswith('(') and cleaned.endswith(')'):
        cleaned = '-' + cleaned[1:-1]
    
    try:
        return float(cleaned)
    except ValueError:
        raise ValueError(f"Unable to parse amount: {amount_str}")


def detect_column_mapping(df: pd.DataFrame) -> Dict[str, str]:
    """
    Auto-detect column names for date, description, amount
    Returns mapping of standard_name -> actual_column_name
    """
    mapping = {}
    
    # Date column detection
    date_keywords = ['date', 'transaction date', 'posted date', 'value date', 'day']
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in date_keywords):
            mapping['date'] = col
            break
    
    # Description column detection
    desc_keywords = ['description', 'details', 'narrative', 'memo', 'particulars', 'transaction']
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in desc_keywords):
            mapping['description'] = col
            break
    
    # Amount column detection (look for debit/credit or single amount)
    amount_keywords = ['amount', 'value', 'transaction amount']
    debit_keywords = ['debit', 'withdrawal', 'spent', 'payment']
    credit_keywords = ['credit', 'deposit', 'received']
    
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in debit_keywords):
            mapping['debit'] = col
        elif any(keyword in col_lower for keyword in credit_keywords):
            mapping['credit'] = col
        elif any(keyword in col_lower for keyword in amount_keywords):
            if 'amount' not in mapping:
                mapping['amount'] = col
    
    return mapping


def normalize_transaction_row(
    row: pd.Series,
    column_mapping: Dict[str, str],
    user_id: int
) -> Dict[str, Any]:
    """
    Normalize a single transaction row from CSV into standard format
    """
    # Extract date
    date_col = column_mapping.get('date')
    if not date_col:
        raise ValueError("Date column not found")
    
    date = normalize_date(str(row[date_col]))
    
    # Extract description
    desc_col = column_mapping.get('description')
    if not desc_col:
        raise ValueError("Description column not found")
    
    description = str(row[desc_col]).strip()
    
    # Extract amount and determine if credit/debit
    is_credit = False
    amount = 0.0
    
    if 'debit' in column_mapping and 'credit' in column_mapping:
        # Separate debit and credit columns
        debit_val = row[column_mapping['debit']]
        credit_val = row[column_mapping['credit']]
        
        # Check which one has a value
        if pd.notna(credit_val) and str(credit_val).strip():
            amount = abs(clean_amount(credit_val))
            is_credit = True
        elif pd.notna(debit_val) and str(debit_val).strip():
            amount = abs(clean_amount(debit_val))
            is_credit = False
        else:
            raise ValueError("No amount found in transaction")
    
    elif 'amount' in column_mapping:
        # Single amount column
        amount_val = clean_amount(row[column_mapping['amount']])
        
        # Positive values are credits, negative are debits
        if amount_val >= 0:
            amount = amount_val
            is_credit = True
        else:
            amount = abs(amount_val)
            is_credit = False
    else:
        raise ValueError("Amount column not found")
    
    # Generate transaction hash
    transaction_hash = generate_transaction_hash(date, description, amount, user_id)
    
    return {
        'date': date,
        'description': description,
        'amount': amount,
        'is_credit': is_credit,
        'transaction_hash': transaction_hash
    }


def parse_csv_transactions(
    file_path: str,
    user_id: int
) -> List[Dict[str, Any]]:
    """
    Parse CSV file and return list of normalized transactions
    """
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        raise ValueError("Unable to read CSV file with any encoding")
    
    # Auto-detect columns
    column_mapping = detect_column_mapping(df)
    
    if not column_mapping.get('date') or not column_mapping.get('description'):
        raise ValueError("Unable to detect required columns (date, description)")
    
    if not column_mapping.get('amount') and not (
        column_mapping.get('debit') and column_mapping.get('credit')
    ):
        raise ValueError("Unable to detect amount columns")
    
    # Parse each row
    transactions = []
    errors = []
    
    for idx, row in df.iterrows():
        try:
            # Skip rows where all values are NaN
            if row.isna().all():
                continue
            
            normalized = normalize_transaction_row(row, column_mapping, user_id)
            transactions.append(normalized)
        except Exception as e:
            errors.append(f"Row {idx + 1}: {str(e)}")
    
    if errors:
        # If more than 50% failed, something is wrong
        if len(errors) > len(df) * 0.5:
            raise ValueError(f"Too many parsing errors: {errors[:5]}")
    
    return transactions
