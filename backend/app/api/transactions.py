from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import tempfile
import os
import hashlib
from app.models.base import get_db
from app.models import User
from app.schemas import (
    TransactionResponse, 
    TransactionUpdate, 
    UploadResponse
)
from app.services.transaction_service import (
    save_transactions,
    update_transaction_category,
    get_user_transactions
)
from app.utils.csv_parser import parse_csv_transactions
from app.utils.pdf_parser import parse_pdf_transactions
from app.api.auth import get_current_user


router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process bank statement (CSV or PDF)
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_ext = file.filename.lower().split('.')[-1]
    if file_ext not in ['csv', 'pdf']:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only CSV and PDF files are supported."
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Generate file hash for duplicate detection
        file_hash = hashlib.md5(content).hexdigest()
        
        # Parse transactions based on file type
        if file_ext == 'csv':
            transactions = parse_csv_transactions(tmp_path, user.id)
        else:  # pdf
            transactions = parse_pdf_transactions(tmp_path, user.id)
        
        if not transactions:
            raise HTTPException(
                status_code=400,
                detail="No valid transactions found in file"
            )
        
        # Save to database
        result = save_transactions(
            db,
            user.id,
            transactions,
            file_hash=file_hash,
            original_file=file.filename
        )
        
        return UploadResponse(
            message=f"Successfully processed {result['transactions_added']} transactions",
            **result
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's transactions with pagination
    """
    transactions = get_user_transactions(db, user.id, limit, offset)
    return transactions


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    update_data: TransactionUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update transaction category (user override)
    """
    if not update_data.category:
        raise HTTPException(status_code=400, detail="Category is required")
    
    try:
        transaction = update_transaction_category(
            db,
            transaction_id,
            update_data.category,
            user.id
        )
        return transaction
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
