#!/usr/bin/env python3
"""
Simple Google Docs Reader MCP Server
"""
from typing import Any, Dict, List, Optional, Callable, Tuple
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import BatchHttpRequest, MediaIoBaseDownload
from mcp.server.fastmcp import FastMCP
import os.path
import pickle
import io
import PyPDF2
import tempfile


# Google Docs API scopes
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]
mcp = FastMCP("google-docs-reader")

def get_credentials() -> Credentials:
    """Get valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    """
    creds = None
    # Use the user's home directory for token storage
    token_path = os.path.join(os.path.expanduser('~'), '.google-docs-token-quoraquora56@gmail.com.pickle')

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds

def get_docs_service():
    """Get the Google Docs service instance."""
    creds = get_credentials()
    return build('docs', 'v1', credentials=creds)

def get_drive_service():
    """Get the Google Drive service instance."""
    creds = get_credentials()
    return build('drive', 'v3', credentials=creds)

@mcp.tool()
async def list_documents() -> List[Dict[str, Any]]:
    """List all Google Docs documents."""
    try:
        service = get_drive_service()
        results = service.files().list(
            fields="files(id, name, mimeType, webViewLink)").execute()
        return results.get('files', [])
    except Exception as e:
        # Return an empty list or a list with an error dict, depending on your needs
        return [{"error": str(e)}]

@mcp.tool()
async def read_pdf_from_drive(file_id: str = '1gV9RCL70OeCGGN0gyaSftKU8VK_OYtvH') -> dict:
    """
    Download a PDF from Google Drive and return its text content.

    Args:
        file_id: The ID of the PDF file on Google Drive.
    """
    try:
        service = get_drive_service()
        # Use a temporary file to store the PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp_file:
            request = service.files().get_media(fileId=file_id)
            downloader = MediaIoBaseDownload(tmp_file, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            tmp_file.flush()

            # Now read the PDF content
            tmp_file.seek(0)
            reader = PyPDF2.PdfReader(tmp_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""

        return {
            "success": True,
            "text": text
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    mcp.run()