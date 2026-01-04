"""Documentation Router - Serve application documentation files.

Provides API endpoints to retrieve user and developer documentation
rendered as HTML from Markdown. These endpoints serve the USER.md and 
DEVELOPER.md files from the documentation/ directory.

Endpoints:
    - GET /docs/user: Retrieve user documentation (HTML)
    - GET /docs/developer: Retrieve developer/technical documentation (HTML)
    - GET /docs/list: List all available documentation files
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
import markdown

from app.config import API_URL

router = APIRouter(prefix="/docs", tags=["documentation"])

# Base path to documentation directory
DOCS_DIR = Path(__file__).parent.parent.parent / "documentation"


def render_markdown_to_html(content: str, title: str) -> str:
    """Convert markdown content to styled HTML.
    
    Args:
        content: Markdown text content
        title: Page title for HTML document
        
    Returns:
        Complete HTML document with styling
    """
    # Convert markdown to HTML
    html_content = markdown.markdown(
        content,
        extensions=[
            'fenced_code',
            'tables',
            'toc',
            'codehilite',
            'nl2br'
        ]
    )
    
    # Wrap in styled HTML template
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - MyBudget Documentation</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
                background-color: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                margin-top: 0;
            }}
            h2 {{
                color: #34495e;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 8px;
                margin-top: 30px;
            }}
            h3 {{
                color: #34495e;
                margin-top: 25px;
            }}
            h4 {{
                color: #555;
                margin-top: 20px;
            }}
            code {{
                background-color: #f8f9fa;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Monaco', 'Courier New', monospace;
                font-size: 0.9em;
                color: #e83e8c;
            }}
            pre {{
                background-color: #2d2d2d;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                border-left: 4px solid #3498db;
            }}
            pre code {{
                background-color: transparent;
                padding: 0;
                color: inherit;
                font-size: 0.85em;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            th {{
                background-color: #3498db;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }}
            td {{
                padding: 12px;
                border-bottom: 1px solid #ecf0f1;
            }}
            tr:hover {{
                background-color: #f8f9fa;
            }}
            blockquote {{
                border-left: 4px solid #3498db;
                padding-left: 20px;
                margin-left: 0;
                color: #555;
                background-color: #f8f9fa;
                padding: 10px 20px;
                border-radius: 4px;
            }}
            a {{
                color: #3498db;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            ul, ol {{
                padding-left: 30px;
            }}
            li {{
                margin: 8px 0;
            }}
            hr {{
                border: none;
                border-top: 2px solid #ecf0f1;
                margin: 30px 0;
            }}
            .nav {{
                background-color: #2c3e50;
                padding: 15px;
                margin: -40px -40px 30px -40px;
                border-radius: 8px 8px 0 0;
            }}
            .nav a {{
                color: white;
                margin-right: 20px;
                font-weight: 500;
            }}
            .nav a:hover {{
                color: #3498db;
            }}
            .badge {{
                background-color: #3498db;
                color: white;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 0.85em;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="{API_URL}/docs/user">User Guide</a>
                <a href="{API_URL}/docs/developer">Developer Guide</a>
                <a href="{API_URL}/docs">API</a>
            </div>
            {html_content}
        </div>
    </body>
    </html>
    """
    return html


@router.get("/user", response_class=HTMLResponse)
def get_user_documentation():
    """Retrieve user documentation.
    
    Returns the contents of USER.md rendered as HTML with styling.
    Includes comprehensive user-facing documentation for the MyBudget application.
    
    Returns:
        HTML rendered documentation
    
    Raises:
        HTTPException: 404 if USER.md file not found
        HTTPException: 500 if error reading file
    """
    try:
        user_doc_path = DOCS_DIR / "USER.md"
        if not user_doc_path.exists():
            raise HTTPException(
                status_code=404,
                detail="User documentation not found"
            )
        
        with open(user_doc_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return render_markdown_to_html(content, "User Guide")
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User documentation not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading user documentation: {str(e)}"
        )


@router.get("/developer", response_class=HTMLResponse)
def get_developer_documentation():
    """Retrieve developer/technical documentation.
    
    Returns the contents of DEVELOPER.md rendered as HTML with styling.
    Includes comprehensive technical documentation for developers working on MyBudget.
    
    Returns:
        HTML rendered documentation
    
    Raises:
        HTTPException: 404 if DEVELOPER.md file not found
        HTTPException: 500 if error reading file
    """
    try:
        dev_doc_path = DOCS_DIR / "DEVELOPER.md"
        if not dev_doc_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Developer documentation not found"
            )
        
        with open(dev_doc_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return render_markdown_to_html(content, "Developer Guide")
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Developer documentation not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading developer documentation: {str(e)}"
        )


@router.get("/list")
def list_documentation():
    """List all available documentation files.
    
    Returns a list of documentation files available in the
    documentation/ directory with their names and descriptions.
    
    Returns:
        List of documentation files with metadata:
            - name: File name
            - endpoint: API endpoint to retrieve the file
            - description: Brief description of the documentation
    """
    docs = []
    
    # User documentation
    user_doc_path = DOCS_DIR / "USER.md"
    if user_doc_path.exists():
        docs.append({
            "name": "USER.md",
            "endpoint": "/docs/user",
            "description": "User-facing documentation for MyBudget application",
            "size_bytes": user_doc_path.stat().st_size
        })
    
    # Developer documentation
    dev_doc_path = DOCS_DIR / "DEVELOPER.md"
    if dev_doc_path.exists():
        docs.append({
            "name": "DEVELOPER.md",
            "endpoint": "/docs/developer",
            "description": "Technical documentation for developers",
            "size_bytes": dev_doc_path.stat().st_size
        })
    
    return {
        "count": len(docs),
        "documentation": docs
    }
