"""
Enhanced PDF Parser for Indian Bank Statements
Uses pdfplumber for better table detection and extraction
Supports HDFC, ICICI, SBI, Axis and other Indian banks
"""

import pdfplumber
from typing import List, Dict, Any
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EnhancedPDFParser:
    """Enhanced PDF parser with table detection and Indian bank support"""
    
    # Indian Rupee amount patterns
    INR_PATTERNS = [
        r'₹\s*(\d[\d,]*\.?\d*)',  # ₹1,234.56
        r'Rs\.?\s*(\d[\d,]*\.?\d*)',  # Rs. 1,234.56
        r'INR\s*(\d[\d,]*\.?\d*)',  # INR 1234.56
    ]
    
    # Date patterns for Indian banks
    DATE_PATTERNS = [
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',  # DD-MM-YYYY or DD/MM/YYYY
        r'(\d{2,4}[-/]\d{1,2}[-/]\d{1,2})',  # YYYY-MM-DD
        r'(\d{1,2}\s+[A-Za-z]{3}\s+\d{2,4})',  # 15 Jan 2024
    ]
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.transactions = []
    
    def parse(self) -> List[Dict[str, Any]]:
        """Main parsing method - tries multiple strategies"""
        try:
            # Strategy 1: Table extraction (most accurate)
            transactions = self._extract_from_tables()
            if transactions and len(transactions) > 0:
                logger.info(f"Extracted {len(transactions)} transactions using table detection")
                return transactions
            
            # Strategy 2: Pattern-based text extraction (fallback)
            transactions = self._extract_from_text()
            if transactions and len(transactions) > 0:
                logger.info(f"Extracted {len(transactions)}transactions using text patterns")
                return transactions
            
            logger.warning("No transactions found in PDF")
            return []
            
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise
    
    def _extract_from_tables(self) -> List[Dict[str, Any]]:
        """Extract transactions from PDF tables using pdfplumber"""
        transactions = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract all tables from the page
                    tables = page.extract_tables()
                    
                    for table_num, table in enumerate(tables):
                        if not table or len(table) < 2:
                            continue
                        
                        # Try to identify header row
                        header_row = self._find_header_row(table)
                        if header_row is None:
                            continue
                        
                        # Map columns
                        column_map = self._map_columns(table[header_row])
                        if not column_map:
                            continue
                        
                        # Extract transactions from rows
                        for row in table[header_row + 1:]:
                            if not row or len(row) < 3:
                                continue
                            
                            transaction = self._parse_table_row(row, column_map)
                            if transaction:
                                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
            return []
    
    def _find_header_row(self, table: List[List[str]]) -> int:
        """Find the header row in a table"""
        header_keywords = ['date', 'description', 'particular', 'narration', 
                          'debit', 'credit', 'withdrawal', 'deposit', 'amount']
        
        for i, row in enumerate(table[:5]):  # Check first 5 rows
            if not row:
                continue
            
            row_text = ' '.join([str(cell).lower() for cell in row if cell])
            
            # Check if row contains multiple header keywords
            matches = sum(1 for keyword in header_keywords if keyword in row_text)
            if matches >= 2:
                return i
        
        return None
    
    def _map_columns(self, header_row: List[str]) -> Dict[str, int]:
        """Map column indices based on header names"""
        column_map = {}
        
        for idx, cell in enumerate(header_row):
            if not cell:
                continue
            
            cell_lower = str(cell).lower().strip()
            
            # Date column
            if any(kw in cell_lower for kw in ['date', 'txn date', 'trans date']):
                column_map['date'] = idx
            
            # Description column
            elif any(kw in cell_lower for kw in ['description', 'particular', 'narration', 'details']):
                column_map['description'] = idx
            
            # Debit column
            elif any(kw in cell_lower for kw in ['debit', 'withdrawal', 'dr']):
                column_map['debit'] = idx
            
            # Credit column
            elif any(kw in cell_lower for kw in ['credit', 'deposit', 'cr']):
                column_map['credit'] = idx
            
            # Single amount column
            elif 'amount' in cell_lower and 'debit' not in column_map and 'credit' not in column_map:
                column_map['amount'] = idx
            
            # Balance column
            elif any(kw in cell_lower for kw in ['balance', 'bal']):
                column_map['balance'] = idx
        
        return column_map
    
    def _parse_table_row(self, row: List[str], column_map: Dict[str, int]) -> Dict[str, Any]:
        """Parse a single table row into a transaction"""
        try:
            # Extract date
            if 'date' not in column_map or column_map['date'] >= len(row):
                return None
            
            date_str = str(row[column_map['date']]).strip()
            if not date_str or date_str == 'None':
                return None
            
            parsed_date = self._normalize_date(date_str)
            if not parsed_date:
                return None
            
            # Extract description
            description = ''
            if 'description' in column_map and column_map['description'] < len(row):
                description = str(row[column_map['description']]).strip()
            
            if not description or description == 'None':
                return None
            
            # Extract amounts
            debit_amount = 0.0
            credit_amount = 0.0
            
            if 'debit' in column_map and column_map['debit'] < len(row):
                debit_str = str(row[column_map['debit']]).strip()
                debit_amount = self._parse_inr_amount(debit_str)
            
            if 'credit' in column_map and column_map['credit'] < len(row):
                credit_str = str(row[column_map['credit']]).strip()
                credit_amount = self._parse_inr_amount(credit_str)
            
            # Handle single amount column (could be + or -)
            if 'amount' in column_map and column_map['amount'] < len(row):
                amount_str = str(row[column_map['amount']]).strip()
                amount = self._parse_inr_amount(amount_str)
                
                # Determine if debit or credit based on sign or keywords
                if amount > 0:
                    if 'dr' in description.lower() or 'debit' in description.lower():
                        debit_amount = amount
                    elif 'cr' in description.lower() or 'credit' in description.lower():
                        credit_amount = amount
                    else:
                        # Default: positive in description = debit
                        debit_amount = amount
            
            # Skip if no amount
            if debit_amount == 0.0 and credit_amount == 0.0:
                return None
            
            # Determine final amount and is_credit flag
            is_credit = credit_amount > 0
            amount = credit_amount if is_credit else debit_amount
            
            return {
                'date': parsed_date,
                'description': description,
                'amount': amount,
                'is_credit': is_credit
            }
            
        except Exception as e:
            logger.debug(f"Error parsing row: {e}")
            return None
    
    def _extract_from_text(self) -> List[Dict[str, Any]]:
        """Fallback: Extract transactions from raw text using patterns"""
        transactions = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    # Try to find transaction lines
                    lines = text.split('\n')
                    for line in lines:
                        transaction = self._parse_text_line(line)
                        if transaction:
                            transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return []
    
    def _parse_text_line(self, line: str) -> Dict[str, Any]:
        """Parse a single line of text for transaction data"""
        # Look for date patterns
        date_match = None
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, line)
            if match:
                date_match = match.group(1)
                break
        
        if not date_match:
            return None
        
        parsed_date = self._normalize_date(date_match)
        if not parsed_date:
            return None
        
        # Look for amounts
        amounts = []
        for pattern in self.INR_PATTERNS:
            matches = re.findall(pattern, line)
            for match in matches:
                amount = self._parse_inr_amount(match)
                if amount > 0:
                    amounts.append(amount)
        
        if not amounts:
            return None
        
        # Determine description (text between date and amount)
        description = line
        for pattern in self.DATE_PATTERNS:
            description = re.sub(pattern, '', description)
        for pattern in self.INR_PATTERNS:
            description = re.sub(pattern, '', description)
        description = description.strip()
        
        if not description:
            return None
        
        # Determine credit/debit
        is_credit = any(kw in line.lower() for kw in ['credit', 'deposit', 'cr'])
        
        return {
            'date': parsed_date,
            'description': description,
            'amount': amounts[0],
            'is_credit': is_credit
        }
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize various date formats to YYYY-MM-DD"""
        date_formats = [
            '%d-%m-%Y', '%d/%m/%Y', '%d-%m-%y', '%d/%m/%y',
            '%Y-%m-%d', '%Y/%m/%d',
            '%d %b %Y', '%d %B %Y',
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def _parse_inr_amount(self, amount_str: str) -> float:
        """Parse INR amount string to float"""
        if not amount_str or amount_str == 'None' or amount_str == '-':
            return 0.0
        
        try:
            # Remove currency symbols and common separators
            cleaned = amount_str.replace('₹', '').replace('Rs', '').replace('Rs.', '')
            cleaned = cleaned.replace('INR', '').replace(',', '').strip()
            
            # Handle negative amounts in parentheses
            if '(' in cleaned and ')' in cleaned:
                cleaned = '-' + cleaned.replace('(', '').replace(')', '')
            
            return abs(float(cleaned))
        except (ValueError, AttributeError):
            return 0.0


def parse_pdf_transactions(pdf_path: str) -> List[Dict[str, Any]]:
    """Main entry point for PDF parsing"""
    parser = EnhancedPDFParser(pdf_path)
    return parser.parse()
