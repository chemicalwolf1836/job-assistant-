def extract_text_from_pdf(file_path: str) -> str:
    text = ""

    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text.strip()
    except ImportError:
        pass
    except Exception as e:
        print(f"pdfplumber failed: {e}, trying pypdf...")

    try:
        import pypdf
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text.strip()
    except ImportError:
        raise ValueError("Neither pdfplumber nor pypdf is installed. Run: pip install pdfplumber pypdf")
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {e}")

    if not text.strip():
        raise ValueError(
            "No text could be extracted from this PDF. "
            "It may be a scanned image — please use a text-based PDF."
        )

    return text.strip()
