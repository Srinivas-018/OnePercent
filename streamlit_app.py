# Minimal Streamlit entrypoint that imports the existing PHT.py app.
# Streamlit Cloud defaults to running streamlit_app.py, so this ensures
# the PHT.py UI is executed as the app.

# If you want PHT.py to pick up a secret API key from Streamlit Cloud's
# secrets, set the secret in the Streamlit Cloud UI as "GEMINI_API_KEY".
# Optionally override PHT.API_KEY here after import if needed.

import os
import streamlit as st

# No heavy logic here; importing PHT will run the app UI code in that module.
# If you want to pass the API key into PHT (PHT defines API_KEY at module level),
# you can set it after import. Note: PHT currently triggers generation logic
# at import time — if you want it to use the secret before any generation runs,
# consider updating PHT.py itself to read st.secrets at the top of the file.

try:
    import PHT  # noqa: F401
except Exception as e:
    st.error(f"Failed to import the main app module PHT.py: {e}")
    raise
