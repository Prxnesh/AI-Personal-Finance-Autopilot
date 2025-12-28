from pypdf import PdfReader
import re
from datetime import datetime
from typing import List, Dict, Any
from .csv_parser import generate_transaction_hash, normalize_date, clean_amount
import tempfile
import os


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Unable to read PDF file: {str(e)}")


def parse_pdf_transactions(
    file_path: str,
    user_id: int
) -> List[Dict[str, Any]]:
    """
    Parse PDF bank statement and extract transactions
    Uses pattern matching for common bank statement formats
    """
    text = extract_text_from_pdf(file_path)
    
    transactions = []
    
    # Common patterns for bank statements
    # Pattern 1: Date Description Amount (most common)
    # Example: 01/12/2023 ATM WITHDRAWAL 500.00
    pattern1 = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(.+?)\s+([\d,]+\.?\d*)\s*(?:Dr|Cr|Debit|Credit)?'
    
    # Pattern 2: Date Amount Description
    # Example: 01/12/2023 500.00 ATM WITHDRAWAL
    pattern2 = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+([\d,]+\.?\d*)\s+(.+?)(?:\n|$)'
    
    # Pattern 3: More detailed, with separate debit/credit columns
    # Example: 01/12/2023 ATM WITHDRAWAL 500.00 -
    pattern3 = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(.+?)\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)'
    
    patterns = [pattern1, pattern2, pattern3]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.MULTILINE)
        
        for match in matches:
            try:
                groups = match.groups()
                
                if len(groups) == 3:
                    # Pattern 1 or 2
                    if '/' in groups[0] or '-' in groups[0]:
                        # groups[0] is date
                        date_str = groups[0]
                        
                        # Determine which is description and which is amount
                        if re.match(r'[\d,]+\.?\d*$', groups[1]):
                            # groups[1] is amount, groups[2] is description
                            amount_str = groups[1]
                            description = groups[2]
                        else:
                            # groups[1] is description, groups[2] is amount
                            description = groups[1]
                            amount_str = groups[2]
                        
                        # Parse values
                        date = normalize_date(date_str)
                        amount = abs(clean_amount(amount_str))
                        
                        # Heuristic: if description contains words like withdrawal, payment, debit -> debit
                        # if contains deposit, credit -> credit
                        debit_keywords = ['withdrawal', 'payment', 'debit', 'purchase', 'transfer out', 'dr']
                        credit_keywords = ['deposit', 'credit', 'received', 'transfer in', 'cr', 'salary']
                        
                        desc_lower = description.lower()
                        is_credit = any(kw in desc_lower for kw in credit_keywords)
                        
                        # If no clear indicator, assume negative is debit
                        if not is_credit:
                            is_credit = False
                        
                        transaction_hash = generate_transaction_hash(date, description, amount, user_id)
                        
                        transactions.append({
                            'date': date,
                            'description': description.strip(),
                            'amount': amount,
                            'is_credit': is_credit,
                            'transaction_hash': transaction_hash
                        })
                
                elif len(groups) == 4:
                    # Pattern 3 with separate debit/credit
                    date_str = groups[0]
                    description = groups[1]
                    debit_str = groups[2]
                    credit_str = groups[3]
                    
                    date = normalize_date(date_str)
                    
                    # Check which column has value
                    try:
                        debit_amount = clean_amount(debit_str)
                        if debit_amount > 0:
                            amount = debit_amount
                            is_credit = False
                        else:
                            raise ValueError()
                    except:
                        try:
                            credit_amount = clean_amount(credit_str)
                            amount = credit_amount
                            is_credit = True
                        except:
                            continue
                    
                    transaction_hash = generate_transaction_hash(date, description, amount, user_id)
                    
                    transactions.append({
                        'date': date,
                        'description': description.strip(),
                        'amount': amount,
                        'is_credit': is_credit,
                        'transaction_hash': transaction_hash
                    })
            
            except Exception:
                # Skip malformed transactions
                continue
        
        # If we found transactions, break
        if transactions:
            break
    
    # Remove duplicates based on transaction hash
    unique_transactions = {}
    for t in transactions:
        unique_transactions[t['transaction_hash']] = t
    
    return list(unique_transactions.values())
