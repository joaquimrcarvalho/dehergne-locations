#!/usr/bin/env python3
"""
PDF to OCR Tool

This script converts PDF pages to images and then OCRs them to extract text.
Uses pdf2image for conversion and pytesseract for OCR.

Requirements:
    pip install pdf2image pytesseract Pillow
    
System dependencies:
    - macOS: brew install poppler tesseract
    - Linux: apt-get install poppler-utils tesseract-ocr
    
Usage:
    python pdf_to_ocr.py input.pdf [output.txt]
"""

import sys
import os
import tempfile
from pathlib import Path
from typing import List, Optional

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        from pdf2image import convert_from_path
    except ImportError:
        print("Error: pdf2image not installed. Run: pip install pdf2image")
        print("Also install poppler: brew install poppler (macOS)")
        sys.exit(1)
    
    try:
        import pytesseract
    except ImportError:
        print("Error: pytesseract not installed. Run: pip install pytesseract")
        print("Also install tesseract: brew install tesseract (macOS)")
        sys.exit(1)
    
    try:
        from PIL import Image
    except ImportError:
        print("Error: Pillow not installed. Run: pip install Pillow")
        sys.exit(1)

def pdf_to_images(pdf_path: str, dpi: int = 300) -> List:
    """Convert PDF pages to PIL Images."""
    from pdf2image import convert_from_path
    
    print(f"Converting PDF to images (DPI={dpi})...")
    images = convert_from_path(pdf_path, dpi=dpi)
    print(f"Converted {len(images)} pages")
    return images

def ocr_image(image, lang: str = 'eng') -> str:
    """OCR a single image and return text."""
    import pytesseract
    
    # Configure tesseract for better accuracy
    custom_config = r'--oem 3 --psm 6'
    
    text = pytesseract.image_to_string(image, lang=lang, config=custom_config)
    return text

def process_pdf(pdf_path: str, output_path: Optional[str] = None, 
                dpi: int = 300, lang: str = 'eng') -> str:
    """
    Process a PDF: convert to images and OCR each page.
    
    Args:
        pdf_path: Path to input PDF
        output_path: Path to output text file (optional)
        dpi: Resolution for image conversion (default 300)
        lang: Language for OCR (default 'eng')
    
    Returns:
        Extracted text from all pages
    """
    check_dependencies()
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)
    
    # Convert PDF to images
    images = pdf_to_images(pdf_path, dpi)
    
    # OCR each page
    all_text = []
    total_pages = len(images)
    
    print(f"\nOCRing {total_pages} pages...")
    for i, image in enumerate(images, 1):
        print(f"  Page {i}/{total_pages}...", end=' ', flush=True)
        page_text = ocr_image(image, lang)
        all_text.append(f"=== Page {i} ===\n{page_text}\n")
        print("✓")
    
    # Combine all text
    full_text = '\n'.join(all_text)
    
    # Save to file if output path provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"\n✓ Text saved to: {output_path}")
    
    return full_text

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_ocr.py <input.pdf> [output.txt]")
        print("\nOptions:")
        print("  --dpi N      Set image resolution (default: 300)")
        print("  --lang CODE  Set OCR language (default: eng)")
        print("\nExamples:")
        print("  python pdf_to_ocr.py document.pdf")
        print("  python pdf_to_ocr.py document.pdf output.txt --dpi 400")
        print("  python pdf_to_ocr.py document.pdf --lang por  # Portuguese")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    
    # Parse options
    dpi = 300
    lang = 'eng'
    
    for i, arg in enumerate(sys.argv):
        if arg == '--dpi' and i + 1 < len(sys.argv):
            dpi = int(sys.argv[i + 1])
        elif arg == '--lang' and i + 1 < len(sys.argv):
            lang = sys.argv[i + 1]
    
    # Process the PDF
    print(f"Processing: {pdf_path}")
    print(f"Settings: DPI={dpi}, Language={lang}")
    print("=" * 60)
    
    text = process_pdf(pdf_path, output_path, dpi, lang)
    
    # Also print first 1000 characters to console
    print("\n" + "=" * 60)
    print("EXTRACTED TEXT PREVIEW:")
    print("=" * 60)
    preview = text[:1000] + "..." if len(text) > 1000 else text
    print(preview)
    
    if not output_path:
        # Save to default filename
        default_output = Path(pdf_path).stem + "_ocr.txt"
        with open(default_output, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"\n✓ Text saved to: {default_output}")

if __name__ == "__main__":
    main()
