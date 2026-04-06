# Google Sheets API Wrapper

FastAPI backend for reading and writing to Google Sheets. Designed to be used by web applications to manage data via Google Sheets as a lightweight database.

## Features

- Fetch data from any Google Sheet (by ID)
- List all sheet tabs
- Add rows with automatic header validation
- Validate data keys against sheet headers before submission
- Export tabs as JSON or a full ZIP archive
- Docker deployment ready — no credentials baked into the image

## Prerequisites

- Python 3.11+
- Google Cloud Service Account credentials (JSON)

## Google Cloud Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the **Google Sheets API**

### 2. Create a Service Account

1. Go to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Give it a name (e.g., `sheet-pipeline`)
4. Grant it the role **Editor** or a custom role with Sheets access
5. Click **Done**

### 3. Download Credentials

1. Find your service account in the list
2. Click on the **Keys** tab
3. Click **Add Key** → **Create new key**
4. Select **JSON** and click **Create**
5. Save the downloaded file — you will pass its contents as an environment variable (see below)

### 4. Share Your Google Sheet

Open your Google Sheet and share it with the service account's email address (the `client_email` field in the JSON file).

Example: `sheet-pipeline@project-id.iam.gserviceaccount.com`

## Configuration

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_CREDENTIALS` | **Yes** | Full JSON content of the service account key file |
| `CONFIG_PATH` | No | Path to `config.yaml` (default: `config.yaml`) |

Set `GOOGLE_CREDENTIALS` by pasting the entire contents of your downloaded JSON key:

```bash
export GOOGLE_CREDENTIALS='{"type":"service_account","project_id":"...","private_key":"-----BEGIN RSA PRIVATE KEY-----\n...","client_email":"...@....iam.gserviceaccount.com",...}'
```

For local development, add it to a `.env` file (already gitignored):

```env
GOOGLE_CREDENTIALS={"type":"service_account","project_id":"..."}
```

### config.yaml

```yaml
default_sheet_index: 0
```

## Local Development

### Using Python

```bash
pip install -r requirements.txt
export GOOGLE_CREDENTIALS='...'
uvicorn main:app --reload --port 8000
```

### Using Docker Compose

```bash
# Set GOOGLE_CREDENTIALS in your shell or a .env file, then:
docker compose up --build
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Version info |
| `GET` | `/health` | Health check |
| `GET` | `/sheets/{sheet_id}` | Fetch sheet data |
| `GET` | `/sheets/{sheet_id}/tabs` | List all tabs |
| `POST` | `/sheets/{sheet_id}/rows` | Add a new row |
| `POST` | `/sheets/{sheet_id}/validate` | Validate keys against headers |
| `GET` | `/sheets/{sheet_id}/export` | Export tab as JSON or all tabs as ZIP |

### GET /sheets/{sheet_id}

Fetch data from a Google Sheet.

**Query Parameters:**
- `tab_name` (optional): Name of the sheet tab. Defaults to the first tab.

**Response:**
```json
{
  "headers": ["Name", "Email", "Phone", "Date"],
  "rows": [
    ["John Doe", "john@example.com", "123-456-7890", "2024-01-01"]
  ],
  "tab_name": "Sheet1",
  "tabs": ["Sheet1", "Sheet2"]
}
```

### GET /sheets/{sheet_id}/tabs

**Response:**
```json
{
  "tabs": ["Sheet1", "Sheet2"]
}
```

### POST /sheets/{sheet_id}/rows

Add a new row to the sheet.

**Query Parameters:**
- `tab_name` (optional): Target tab. Defaults to the first tab.

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

**Success Response:**
```json
{
  "success": true,
  "row_index": 3
}
```

**Validation Error Response:**
```json
{
  "success": false,
  "error": "Invalid data keys",
  "missing_keys": ["Date"],
  "extra_keys": ["InvalidColumn"]
}
```

### POST /sheets/{sheet_id}/validate

Validate data keys against sheet headers without writing any data.

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

### GET /sheets/{sheet_id}/export

**Query Parameters:**
- `tab_name` (optional): Export a single tab as a JSON file. If omitted, exports all tabs as a ZIP archive.

Returns a downloadable `{tab_name}.json` or `export.zip`.

## Usage Examples

### cURL

```bash
# Health check
curl http://localhost:8000/health

# Fetch sheet data
curl "http://localhost:8000/sheets/YOUR_SHEET_ID"

# Fetch specific tab
curl "http://localhost:8000/sheets/YOUR_SHEET_ID?tab_name=Sheet2"

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

# Export a tab as JSON
curl "http://localhost:8000/sheets/YOUR_SHEET_ID/export?tab_name=Sheet1" -o Sheet1.json

# Export all tabs as ZIP
curl "http://localhost:8000/sheets/YOUR_SHEET_ID/export" -o export.zip
```

### JavaScript

```javascript
const API_URL = 'http://localhost:8000';
const SHEET_ID = 'YOUR_SHEET_ID';

// Fetch sheet data
const res = await fetch(`${API_URL}/sheets/${SHEET_ID}`);
const data = await res.json();

// Add a row
await fetch(`${API_URL}/sheets/${SHEET_ID}/rows`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    data: { Name: 'John Doe', Email: 'john@example.com', Phone: '123-456-7890' }
  })
});
```

## Docker Deployment

Credentials are injected at runtime — the image contains no secrets and is safe to push to a public registry.

```bash
# Build
docker build -t sheets-api .

# Run
docker run -p 8000:8000 -e GOOGLE_CREDENTIALS="$GOOGLE_CREDENTIALS" sheets-api
```

Or with Docker Compose (reads `GOOGLE_CREDENTIALS` from your shell or `.env`):

```bash
docker compose up --build
```

## Project Structure

```
sheet-pipeline/
├── config.py           # Configuration and credential loader
├── config.yaml         # App configuration
├── models.py           # Pydantic request/response schemas
├── sheets_client.py    # Google Sheets API client
├── main.py             # FastAPI application and endpoints
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Docker Compose setup
├── .gitignore
├── .dockerignore
└── README.md
```


## License

MIT
