from typing import Optional

from pydantic import BaseModel


class RowData(BaseModel):
    data: dict


class SheetData(BaseModel):
    headers: list[str]
    rows: list[list[str]]
    tab_name: str
    tabs: list[str]


class TabsResponse(BaseModel):
    tabs: list[str]


class AddRowRequest(BaseModel):
    data: dict


class AddRowResponse(BaseModel):
    success: bool
    row_index: Optional[int] = None
    error: Optional[str] = None
    missing_keys: Optional[list[str]] = None
    extra_keys: Optional[list[str]] = None


class ValidateRequest(BaseModel):
    data: dict


class ValidateResponse(BaseModel):
    valid: bool
    missing_keys: list[str]
    extra_keys: list[str]
