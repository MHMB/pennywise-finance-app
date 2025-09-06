import pandas as pd
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Tuple, Optional
import logging
from io import StringIO

logger = logging.getLogger(__name__)

# Category mapping based on keywords
CATEGORY_KEYWORDS = {
    'Food': ['restaurant', 'food', 'grocery', 'supermarket', 'dining', 'cafe', 'coffee', 'lunch', 'dinner', 'breakfast'],
    'Transportation': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'train', 'metro', 'parking', 'toll'],
    'Entertainment': ['movie', 'cinema', 'netflix', 'spotify', 'game', 'concert', 'theater', 'entertainment'],
    'Shopping': ['amazon', 'store', 'shop', 'clothing', 'fashion', 'electronics', 'retail'],
    'Healthcare': ['doctor', 'hospital', 'pharmacy', 'medical', 'health', 'dental', 'clinic'],
    'Utilities': ['electric', 'water', 'gas bill', 'internet', 'phone', 'utility', 'cable'],
    'Rent': ['rent', 'housing', 'apartment', 'mortgage', 'lease'],
    'Insurance': ['insurance', 'premium', 'policy'],
    'Education': ['school', 'education', 'tuition', 'book', 'course', 'university'],
    'Income': ['salary', 'wage', 'bonus', 'income', 'payroll', 'deposit', 'refund']
}

def detect_csv_format(csv_content: str) -> Dict[str, str]:
    """
    Detect CSV format and return column mappings
    """
    lines = csv_content.strip().split('\n')
    if not lines:
        return {}
    
    # Try to detect delimiter
    delimiter = ','
    if ';' in lines[0] and ',' not in lines[0]:
        delimiter = ';'
    elif '\t' in lines[0]:
        delimiter = '\t'
    
    # Read first few lines to understand structure
    df_sample = pd.read_csv(StringIO(csv_content), delimiter=delimiter, nrows=5)
    
    # Common column name mappings
    column_mappings = {
        'date': ['date', 'transaction_date', 'trans_date', 'posted_date', 'timestamp'],
        'amount': ['amount', 'value', 'sum', 'total', 'debit', 'credit'],
        'description': ['description', 'desc', 'memo', 'details', 'narration', 'reference'],
        'category': ['category', 'cat', 'type', 'classification']
    }
    
    detected_columns = {}
    for standard_name, possible_names in column_mappings.items():
        for col in df_sample.columns:
            if any(name.lower() in col.lower() for name in possible_names):
                detected_columns[standard_name] = col
                break
    
    return {
        'delimiter': delimiter,
        'columns': detected_columns,
        'sample_data': df_sample.head(2).to_dict('records')
    }

def parse_amount(amount_str: str) -> Optional[Decimal]:
    """
    Parse amount string to Decimal, handling various formats
    """
    if pd.isna(amount_str) or amount_str == '':
        return None
    
    # Remove currency symbols and whitespace
    amount_str = str(amount_str).strip()
    amount_str = re.sub(r'[^\d.,\-]', '', amount_str)
    
    # Handle different decimal separators
    if ',' in amount_str and '.' in amount_str:
        # European format: 1.234,56
        if amount_str.rfind(',') > amount_str.rfind('.'):
            amount_str = amount_str.replace('.', '').replace(',', '.')
        # US format: 1,234.56
        else:
            amount_str = amount_str.replace(',', '')
    elif ',' in amount_str:
        # Check if it's decimal separator or thousands separator
        parts = amount_str.split(',')
        if len(parts) == 2 and len(parts[1]) <= 2:
            # Decimal separator
            amount_str = amount_str.replace(',', '.')
        else:
            # Thousands separator
            amount_str = amount_str.replace(',', '')
    
    try:
        return Decimal(amount_str)
    except (InvalidOperation, ValueError):
        return None

def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string to datetime, handling various formats
    """
    if pd.isna(date_str) or date_str == '':
        return None
    
    date_str = str(date_str).strip()
    
    # Common date formats
    date_formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%d-%m-%Y',
        '%m-%d-%Y',
        '%Y/%m/%d',
        '%d.%m.%Y',
        '%m.%d.%Y',
        '%Y.%m.%d',
        '%d %m %Y',
        '%m %d %Y',
        '%Y %m %d'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Try pandas parsing as fallback
    try:
        return pd.to_datetime(date_str)
    except:
        return None

def categorize_transaction(description: str, amount: Decimal) -> str:
    """
    Auto-categorize transaction based on description and amount
    """
    if not description:
        return 'Uncategorized'
    
    description_lower = description.lower()
    
    # Check for income indicators
    if amount > 0:
        for keyword in CATEGORY_KEYWORDS['Income']:
            if keyword in description_lower:
                return 'Income'
    
    # Check expense categories
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == 'Income':
            continue
        for keyword in keywords:
            if keyword in description_lower:
                return category
    
    return 'Uncategorized'

def process_csv_file(csv_content: str, user_id: int) -> Dict:
    """
    Process CSV file and return processed transactions
    """
    try:
        # Detect format
        format_info = detect_csv_format(csv_content)
        if not format_info.get('columns'):
            return {
                'success': False,
                'error': 'Could not detect CSV format. Please ensure your CSV has columns for date, amount, and description.',
                'transactions': []
            }
        
        # Read CSV with detected format
        delimiter = format_info['delimiter']
        df = pd.read_csv(StringIO(csv_content), delimiter=delimiter)
        
        # Map columns
        columns = format_info['columns']
        required_columns = ['date', 'amount', 'description']
        
        if not all(col in columns for col in required_columns):
            return {
                'success': False,
                'error': f'Missing required columns. Found: {list(columns.keys())}, Required: {required_columns}',
                'transactions': []
            }
        
        processed_transactions = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Parse date
                date_value = parse_date(row[columns['date']])
                if not date_value:
                    errors.append(f"Row {index + 1}: Invalid date format")
                    continue
                
                # Parse amount
                amount_value = parse_amount(row[columns['amount']])
                if amount_value is None:
                    errors.append(f"Row {index + 1}: Invalid amount format")
                    continue
                
                # Get description
                description = str(row[columns['description']]).strip()
                if not description:
                    errors.append(f"Row {index + 1}: Missing description")
                    continue
                
                # Determine if it's income or expense
                is_income = amount_value > 0
                
                # Auto-categorize
                category = 'Uncategorized'
                if columns.get('category') and row[columns['category']]:
                    category = str(row[columns['category']]).strip()
                else:
                    category = categorize_transaction(description, amount_value)
                
                # Create transaction data
                transaction_data = {
                    'user_id': user_id,
                    'date': date_value.date(),
                    'amount': abs(amount_value),  # Store as positive value
                    'description': description,
                    'category': category,
                    'is_income': is_income
                }
                
                processed_transactions.append(transaction_data)
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
                continue
        
        return {
            'success': True,
            'transactions': processed_transactions,
            'errors': errors,
            'total_rows': len(df),
            'processed_rows': len(processed_transactions),
            'error_count': len(errors)
        }
        
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        return {
            'success': False,
            'error': f'Error processing CSV file: {str(e)}',
            'transactions': []
        }

def validate_csv_data(transactions: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """
    Validate processed transaction data
    """
    valid_transactions = []
    errors = []
    
    for i, transaction in enumerate(transactions):
        try:
            # Validate required fields
            required_fields = ['date', 'amount', 'description', 'category']
            for field in required_fields:
                if field not in transaction or not transaction[field]:
                    errors.append(f"Transaction {i + 1}: Missing {field}")
                    continue
            
            # Validate amount
            if not isinstance(transaction['amount'], Decimal) or transaction['amount'] <= 0:
                errors.append(f"Transaction {i + 1}: Invalid amount")
                continue
            
            # Validate date
            if not isinstance(transaction['date'], datetime.date):
                errors.append(f"Transaction {i + 1}: Invalid date")
                continue
            
            valid_transactions.append(transaction)
            
        except Exception as e:
            errors.append(f"Transaction {i + 1}: {str(e)}")
    
    return valid_transactions, errors