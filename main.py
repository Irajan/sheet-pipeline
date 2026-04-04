from typing import Optional
import json
import zipfile
from io import BytesIO

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response

from models import (
    AddRowRequest,
    AddRowResponse,
    SheetData,
    TabsResponse,
    ValidateRequest,
    ValidateResponse,
)
from sheets_client import SheetsClient

app = FastAPI(
    title="Google Sheets API",
    description="API wrapper for Google Sheets - read and write data",
    version="1.0.0",
)

_client = SheetsClient()


@app.get("/")
def root():
    return {"message": "Google Sheets API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/sheets/{sheet_id}", response_model=SheetData)
def get_sheet_data(
    sheet_id: str,
    tab_name: Optional[str] = Query(None, description="Sheet tab name"),
):
    try:
        print(f"Fetching data for sheet_id: {sheet_id}, tab_name: {tab_name}")
        return _client.get_sheet_data(sheet_id, tab_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error fetching sheet data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching sheet: {str(e)}")


@app.get("/sheets/{sheet_id}/tabs", response_model=TabsResponse)
def get_tabs(sheet_id: str):
    try:
        tabs = _client.list_tabs(sheet_id)
        return TabsResponse(tabs=tabs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tabs: {str(e)}")


@app.post("/sheets/{sheet_id}/rows", response_model=AddRowResponse)
def add_row(
    sheet_id: str,
    request: AddRowRequest,
    tab_name: Optional[str] = Query(None, description="Sheet tab name"),
):
    try:
        result = _client.append_row(sheet_id, request.data, tab_name)
        return AddRowResponse(
            success=result.get("success", False),
            row_index=result.get("row_index"),
            error=result.get("error"),
            missing_keys=result.get("missing_keys"),
            extra_keys=result.get("extra_keys"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding row: {str(e)}")


@app.post("/sheets/{sheet_id}/validate", response_model=ValidateResponse)
def validate_data(
    sheet_id: str,
    request: ValidateRequest,
    tab_name: Optional[str] = Query(None, description="Sheet tab name"),
):
    try:
        result = _client.validate_keys(sheet_id, request.data, tab_name)
        return ValidateResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error validating data: {str(e)}"
        )


@app.get("/sheets/{sheet_id}/export")
def export_sheet(
    sheet_id: str,
    tab_name: Optional[str] = Query(None, description="Export specific tab as JSON"),
):
    try:
        if tab_name:
            data = _client.get_sheet_data(sheet_id, tab_name)
            headers = data["headers"]
            rows = data["rows"]
            
            formatted_rows = []
            for row in rows:
                row_dict = {}
                for i, header in enumerate(headers):
                    row_dict[header] = row[i] if i < len(row) else ""
                formatted_rows.append(row_dict)
            
            json_data = formatted_rows
            json_str = json.dumps(json_data, indent=2)
            return Response(
                content=json_str,
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={tab_name}.json"}
            )
        
        all_tabs = _client.get_all_tabs_data(sheet_id)
        
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for tab_name, tab_data in all_tabs.items():
                json_str = json.dumps(tab_data, indent=2)
                file_name = f"{tab_name}.json"
                zf.writestr(file_name, json_str)
        
        buffer.seek(0)
        return Response(
            content=buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=export.zip"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting sheet: {str(e)}")
