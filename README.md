# Google Sheets API Wrapper

FastAPI backend for reading and writing to Google Sheets. Designed to be used by web applications to manage data via Google Sheets as a database.

## Features

- Fetch data from any Google Sheet (by ID)
- List all sheet tabs
- Add rows with validation (ensures JSON keys match sheet headers)
- Validate data before submission
- Docker deployment ready

## Prerequisites

- Python 3.11+
- Google Cloud Service Account credentials

## Google Cloud Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the **Google Sheets API**

### 2. Create Service Account

1. Go to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Give it a name (e.g., `sheet-pipeline`)
4. Grant it the role **Service Account User**
5. Click **Done**

### 3. Download Credentials

1. Find your service account in the list
2. Click on the **Keys** tab
3. Click **Add Key** → **Create new key**
4. Select **JSON** and click Create
5. Download the file and save it as `credentials.json` in the `/app` folder

### 4. Share Your Google Sheet

Open your Google Sheet and share it with the service account email address found in your `credentials.json` file (the `client_email` field).

Example: `sheet-pipeline@project-id.iam.gserviceaccount.com`

## Configuration

Edit `config.yaml` in the `/app` folder:

```yaml
credentials_path: "credentials.json"
default_sheet_index: 0
```

## Local Development

### Using Python

```bash
cd app
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Using Docker

```bash
cd app
docker-compose up --build
```

The API will be available at `http://localhost:8000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/sheets/{sheet_id}` | Fetch all sheet data |
| `GET` | `/sheets/{sheet_id}/tabs` | List all sheet tabs |
| `POST` | `/sheets/{sheet_id}/rows` | Add a new row (validates keys first) |
| `POST` | `/sheets/{sheet_id}/validate` | Validate JSON keys against sheet headers |

### GET /sheets/{sheet_id}

Fetch data from a Google Sheet.

**Query Parameters:**
- `sheet_name` (optional): Name of the sheet tab. Defaults to the first tab.

**Response:**
```json
{
  "headers": ["Name", "Email", "Phone", "Date"],
  "rows": [
    ["John Doe", "john@example.com", "123-456-7890", "2024-01-01"],
    ["Jane Smith", "jane@example.com", "987-654-3210", "2024-01-02"]
  ],
  "tab_name": "Sheet1",
  "tabs": ["Sheet1", "Sheet2"]
}
```

### POST /sheets/{sheet_id}/rows

Add a new row to the sheet.

**Request Body:**
```json
{
  "data": {
    "Name": "John Doe",
    "Email": "john@example.com",
    "Phone": "123-456-7890",
    "Date": "2024-01-01"
  }
}
```

**Response:**
```json
{
  "success": true,
  "row_index": 3
}
```

**Error Response (invalid keys):**
```json
{
  "success": false,
  "error": "Invalid data keys",
  "missing_keys": ["Date"],
  "extra_keys": ["InvalidColumn"]
}
```

### POST /sheets/{sheet_id}/validate

Validate JSON keys against sheet headers without adding a row.

**Request Body:**
```json
{
  "data": {
    "Name": "John Doe",
    "Email": "john@example.com"
  }
}
```

**Response:**
```json
{
  "valid": false,
  "missing_keys": ["Phone", "Date"],
  "extra_keys": []
}
```

## Usage Example

### Using cURL

```bash
# Fetch sheet data
curl "http://localhost:8000/sheets/YOUR_SHEET_ID"

# List tabs
curl "http://localhost:8000/sheets/YOUR_SHEET_ID/tabs"

# Add a row
curl -X POST "http://localhost:8000/sheets/YOUR_SHEET_ID/rows" \
  -H "Content-Type: application/json" \
  -d '{"data": {"Name": "John", "Email": "john@example.com", "Phone": "123"}}'

# Validate data
curl -X POST "http://localhost:8000/sheets/YOUR_SHEET_ID/validate" \
  -H "Content-Type: application/json" \
  -d '{"data": {"Name": "John", "Email": "john@example.com"}}'
```

### Using JavaScript

```javascript
const API_URL = 'http://localhost:8000';

// Fetch sheet data
const response = await fetch(`${API_URL}/sheets/YOUR_SHEET_ID`);
const data = await response.json();

// Add a row
const result = await fetch(`${API_URL}/sheets/YOUR_SHEET_ID}/rows`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    data: {
      name: 'John Doe',
      email: 'john@example.com',
      phone: '123-456-7890'
    }
  })
});
```

## Docker Deployment

### Build

```bash
cd app
docker build -t sheets-api .
```

### Run

```bash
docker run -p 8000:8000 sheets-api
```

Or use docker-compose:

```bash
cd app
docker-compose up --build
```

### Environment Variables

You can override the config using environment variables:

- `CONFIG_PATH`: Path to config.yaml (default: `config.yaml`)

## Project Structure

```
sheet-pipeline/
├── app/                    # FastAPI Backend
│   ├── config.py          # Configuration loader
│   ├── config.yaml        # App configuration
│   ├── credentials.json   # Google Service Account (user provides)
│   ├── models.py          # Pydantic schemas
│   ├── sheets_client.py   # Google Sheets API client
│   ├── main.py            # FastAPI endpoints
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # Docker image
│   ├── docker-compose.yml # Docker Compose
│   └── README.md          # This file
```

## License

MIT
