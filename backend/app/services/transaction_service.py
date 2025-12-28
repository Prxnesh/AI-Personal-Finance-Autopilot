from sqlalchemy.orm import Session
from typing import List, Dict, Any
import hashlib
from datetime import datetime
from app.models import Transaction, Category
from app.ai.categorizer import HybridCategorizer



def save_transactions(
    db: Session,
    user_id: int,
    transactions: List[Dict[str, Any]],
    file_hash: str = None,
    original_file: str = None
) -> Dict[str, Any]:
    """
    Save transactions to database with categorization
    Returns: dict with processing stats
    """
    # Load learned patterns from database
    learned_patterns = {}
    category_records = db.query(Category).filter(Category.user_id == user_id).all()
    for record in category_records:
        learned_patterns[record.description_pattern.lower()] = record.learned_category
    
    # Initialize categorizer
    categorizer = HybridCategorizer(learned_patterns)
    
    # Process each transaction
    added = 0
    duplicates = 0
    errors = []
    
    for trans_data in transactions:
        try:
            # Check for duplicate
            existing = db.query(Transaction).filter(
                Transaction.transaction_hash == trans_data['transaction_hash']
            ).first()
            
            if existing:
                duplicates += 1
                continue
            
            # Categorize
            category, confidence = categorizer.categorize(
                trans_data['description'],
                trans_data['is_credit']
            )
            
            # Create transaction
            transaction = Transaction(
                user_id=user_id,
                date=trans_data['date'],
                description=trans_data['description'],
                amount=trans_data['amount'],
                is_credit=trans_data['is_credit'],
                category=category,
                category_confidence=confidence,
                transaction_hash=trans_data['transaction_hash'],
                file_hash=file_hash,
                original_file=original_file
            )
            
            db.add(transaction)
            added += 1
        
        except Exception as e:
            errors.append(f"Transaction error: {str(e)}")
    
    # Commit all transactions
    db.commit()
    
    return {
        "transactions_processed": len(transactions),
        "transactions_added": added,
        "duplicates_skipped": duplicates,
        "errors": errors
    }


def update_transaction_category(
    db: Session,
    transaction_id: int,
    new_category: str,
    user_id: int
) -> Transaction:
    """
    Update transaction category and learn from user override
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user_id
    ).first()
    
    if not transaction:
        raise ValueError("Transaction not found")
    
    # Update category
    old_category = transaction.category
    transaction.category = new_category
    transaction.user_overridden = True
    transaction.category_confidence = 1.0
    
    # Learn from this override
    desc_pattern = transaction.description.lower().strip()
    
    # Check if pattern exists
    category_record = db.query(Category).filter(
        Category.user_id == user_id,
        Category.description_pattern == desc_pattern
    ).first()
    
    if category_record:
        category_record.learned_category = new_category
        category_record.usage_count += 1
    else:
        category_record = Category(
            user_id=user_id,
            description_pattern=desc_pattern,
            learned_category=new_category,
            confidence=1.0,
            usage_count=1
        )
        db.add(category_record)
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


def get_user_transactions(
    db: Session,
    user_id: int,
    limit: int = 100,
    offset: int = 0
) -> List[Transaction]:
    """
    Get user's transactions with pagination
    """
    return db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(Transaction.date.desc()).limit(limit).offset(offset).all()


def get_transactions_by_category(
    db: Session,
    user_id: int,
    category: str
) -> List[Transaction]:
    """
    Get transactions for a specific category
    """
    return db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.category == category
    ).order_by(Transaction.date.desc()).all()
