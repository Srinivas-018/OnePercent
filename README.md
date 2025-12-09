# OnePercent — Habit Master Tracker (Streamlit)

This repository contains a Streamlit habit tracker (PHT.py). These extra files make it simple to deploy to Streamlit Cloud.

## Files added for deployment
- `streamlit_app.py` — default Streamlit Cloud entrypoint (imports your existing `PHT.py`).
- `requirements.txt` — Python dependencies required on the server.
- `.streamlit/config.toml` — Streamlit server configuration.
- `.streamlit/secrets.toml.example` — example of secrets layout (do not commit actual secrets).
- `Procfile` — optional explicit run command (harmless to include).
- `.gitignore` — recommended ignores.

## How to deploy on Streamlit Cloud

1. Commit and push these files to your repository on GitHub.

2. Create a new app in Streamlit Cloud:
   - Connect your GitHub account.
   - Select this repository and the branch you pushed to.
   - Streamlit Cloud will normally detect `streamlit_app.py` automatically. If it doesn't, set the main file to `streamlit_app.py`.

3. Add your Gemini / API key securely:
   - In Streamlit Cloud, open your app -> Settings -> Secrets.
   - Add a secret named `GEMINI_API_KEY` with your API key value.
   - Do NOT commit secrets to the repository.

4. (Optional) If you want the app to use the secret, update `PHT.py` to read the key from `st.secrets` or environment variables. Right now `PHT.py` defines an empty API_KEY string at the top; you'll want to replace or override it at runtime. Example modification inside `PHT.py` near the top (recommended):

```python
import os
import streamlit as st

# Preferred: use st.secrets (Streamlit Cloud secrets) first, then env var fallback
API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""
```

5. Deploy. Streamlit Cloud will install packages from `requirements.txt` and run `streamlit_app.py`.

## Notes & Caution
- Do not commit real API keys to the git repository.
- If you modify `PHT.py` to read from `st.secrets`, the app will use the secret from Streamlit Cloud automatically.
- If you need help adjusting `PHT.py` to pull the key from secrets, I can update that file for you as well.

Happy deploying!
