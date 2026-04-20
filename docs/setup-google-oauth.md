# Google OAuth Setup

YouTube Studio MCP uses your own Google Cloud OAuth client. This keeps API access under your control and avoids sharing channel credentials with a hosted service.

## 1. Create or choose a Google Cloud project

Open the Google Cloud Console and create a new project, or choose an existing project dedicated to YouTube automation.

## 2. Enable APIs

Enable these APIs for the project:

- YouTube Data API v3
- YouTube Analytics API

## 3. Configure OAuth consent

Create or update the OAuth consent screen. For personal use, an external testing app is usually enough. Add your own Google account as a test user if the app is not verified.

## 4. Create OAuth credentials

Create an OAuth client ID with application type `Desktop app`.

Download the JSON file and save it locally as:

```text
secrets/client_secret.json
```

## 5. Authenticate locally

Run:

```bash
python3 scripts/auth.py auth
```

Your browser will open a Google OAuth page. After you approve access, a local token will be written to:

```text
secrets/token.json
```

Both files are ignored by git and should stay on your machine.
