from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build

from config import get_credentials_info


class SheetsClient:
    def __init__(self):
        self._service = None
        self._credentials = None

    def _get_service(self):
        if self._service is None:
            creds = service_account.Credentials.from_service_account_info(
                get_credentials_info(),
                scopes=["https://www.googleapis.com/auth/spreadsheets"],
            )
            self._service = build("sheets", "v4", credentials=creds)
        return self._service

    def _get_spreadsheet(self, spreadsheet_id: str):
        service = self._get_service()
        return service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

    def _match_header(self, key: str, headers: list[str]) -> Optional[str]:
        if key in headers:
            return key

        key_lower = key.lower()
        matches = [h for h in headers if h.lower() == key_lower]

        if not matches:
            return None

        if len(matches) == 1:
            return matches[0]

        first_char = key[0] if key else ""
        first_char_is_upper = first_char.isupper()

        for header in matches:
            if header and header[0].isupper() == first_char_is_upper:
                return header

        return matches[0]

    def list_tabs(self, spreadsheet_id: str) -> list[str]:
        spreadsheet = self._get_spreadsheet(spreadsheet_id)
        sheets = spreadsheet.get("sheets", [])
        return [sheet.get("properties", {}).get("title", "Sheet1") for sheet in sheets]

    def get_sheet_data(
        self, spreadsheet_id: str, sheet_name: Optional[str] = None
    ) -> dict:
        spreadsheet = self._get_spreadsheet(spreadsheet_id)
        sheets = spreadsheet.get("sheets", [])

        if sheet_name is None:
            sheet = sheets[0]
            sheet_name = sheet.get("properties", {}).get("title", "Sheet1")
        else:
            sheet = None
            for s in sheets:
                if s.get("properties", {}).get("title") == sheet_name:
                    sheet = s
                    break
            if sheet is None:
                raise ValueError(f"Sheet '{sheet_name}' not found")

        sheet_id = sheet.get("properties", {}).get("sheetId")

        range_name = f"{sheet_name}!A:Z"
        result = (
            self._get_service()
            .spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )

        values = result.get("values", [])
        headers = values[0] if values else []
        rows = values[1:] if len(values) > 1 else []

        return {
            "headers": headers,
            "rows": rows,
            "tab_name": sheet_name,
            "tabs": self.list_tabs(spreadsheet_id),
        }

    def get_all_tabs_data(self, spreadsheet_id: str) -> dict:
        tabs = self.list_tabs(spreadsheet_id)
        all_data = {}
        
        for tab in tabs:
            data = self.get_sheet_data(spreadsheet_id, tab)
            headers = data["headers"]
            rows = data["rows"]
            
            formatted_rows = []
            for row in rows:
                row_dict = {}
                for i, header in enumerate(headers):
                    row_dict[header] = row[i] if i < len(row) else ""
                formatted_rows.append(row_dict)
            
            all_data[tab] = formatted_rows
        
        return all_data

    def validate_keys(
        self, spreadsheet_id: str, data: dict, sheet_name: Optional[str] = None
    ) -> dict:
        sheet_data = self.get_sheet_data(spreadsheet_id, sheet_name)
        headers = sheet_data["headers"]

        matched_headers = set()
        extra_keys = []

        for key in data.keys():
            matched = self._match_header(key, headers)
            if matched:
                matched_headers.add(matched)
            else:
                extra_keys.append(key)

        missing_keys = [h for h in headers if h not in matched_headers]

        return {
            "valid": len(missing_keys) == 0 and len(extra_keys) == 0,
            "missing_keys": missing_keys,
            "extra_keys": extra_keys,
        }

    def append_row(
        self,
        spreadsheet_id: str,
        row_data: dict,
        sheet_name: Optional[str] = None,
    ) -> dict:
        sheet_data = self.get_sheet_data(spreadsheet_id, sheet_name)
        headers = sheet_data["headers"]

        key_to_header = {}
        extra_keys = []

        for key in row_data.keys():
            matched = self._match_header(key, headers)
            if matched:
                is_exact = key == matched
                key_to_header[key] = (matched, is_exact)
            else:
                extra_keys.append(key)

        matched_headers = set(v[0] for v in key_to_header.values())
        missing_keys = [h for h in headers if h not in matched_headers]

        row_values = []
        for h in headers:
            value = ""
            exact_match_value = ""
            fallback_match_value = ""

            for key, (matched_header, is_exact) in key_to_header.items():
                if matched_header == h:
                    if is_exact:
                        exact_match_value = row_data.get(key, "")
                    else:
                        fallback_match_value = row_data.get(key, "")

            value = exact_match_value if exact_match_value else fallback_match_value
            row_values.append(value)

        range_name = f"{sheet_data['tab_name']}!A{len(sheet_data['rows']) + 2}"

        body = {"values": [row_values]}

        result = (
            self._get_service()
            .spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )

        return {
            "success": True,
            "row_index": len(sheet_data["rows"]) + 2,
            "missing_keys": missing_keys if missing_keys else None,
            "extra_keys": extra_keys if extra_keys else None,
        }
