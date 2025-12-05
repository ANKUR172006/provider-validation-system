"""
File handling utilities for CSV and PDF processing
"""
import os
import csv
import json
import uuid
from typing import List, Dict, Any
from pathlib import Path
import aiofiles
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import pandas as pd


async def save_uploaded_file(file_content: bytes, filename: str, upload_dir: str) -> str:
    """Save uploaded file and return file path"""
    os.makedirs(upload_dir, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_ext = Path(filename).suffix
    file_path = os.path.join(upload_dir, f"{file_id}{file_ext}")
    
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)
    
    return file_path


async def read_csv_file(file_path: str) -> List[Dict[str, Any]]:
    """Read CSV file and return list of dictionaries"""
    try:
        df = pd.read_csv(file_path)
        # Convert DataFrame to list of dictionaries
        records = df.to_dict('records')
        return records
    except Exception as e:
        raise Exception(f"Error reading CSV file: {str(e)}")


async def extract_pdf_text(file_path: str) -> str:
    """Extract text from PDF using OCR"""
    try:
        # Try direct PDF text extraction first (faster)
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                if text.strip():
                    return text
        except:
            pass
        
        # Fallback to OCR if direct extraction fails
        images = convert_from_path(file_path, dpi=300)
        full_text = ""
        for image in images:
            text = pytesseract.image_to_string(image)
            full_text += text + "\n"
        
        return full_text
    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")


def parse_provider_from_text(text: str) -> Dict[str, Any]:
    """Parse provider information from extracted text"""
    # Simple parsing logic - can be enhanced with NLP
    provider = {
        "name": "",
        "npi": "",
        "specialty": "",
        "phone": "",
        "email": "",
        "address": "",
        "city": "",
        "state": "",
        "zip_code": "",
        "website": ""
    }
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Extract NPI (10-digit number)
        import re
        npi_match = re.search(r'\b\d{10}\b', line)
        if npi_match and not provider["npi"]:
            provider["npi"] = npi_match.group()
        
        # Extract phone
        phone_match = re.search(r'(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', line)
        if phone_match and not provider["phone"]:
            provider["phone"] = re.sub(r'[^\d]', '', phone_match.group())
        
        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line)
        if email_match and not provider["email"]:
            provider["email"] = email_match.group()
        
        # Extract website
        url_match = re.search(r'https?://[^\s]+', line)
        if url_match and not provider["website"]:
            provider["website"] = url_match.group()
        
        # Extract address components
        if any(word in line.lower() for word in ['street', 'st', 'avenue', 'ave', 'road', 'rd', 'drive', 'dr']):
            provider["address"] = line
        
        # Extract state and zip
        state_zip_match = re.search(r'([A-Z]{2})\s+(\d{5}(-\d{4})?)', line)
        if state_zip_match:
            provider["state"] = state_zip_match.group(1)
            provider["zip_code"] = state_zip_match.group(2)
    
    return provider

