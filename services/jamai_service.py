import streamlit as st
import tempfile
import os
from jamaibase import JamAI, protocol as p

# ==========================================
# 🔧 CONFIGURATION (MATCH THIS TO YOUR JAMAI TABLES)
# ==========================================

# 1. Project Credentials
PROJECT_ID = "proj_ca6a5b4d055773835bd8afba" 

# 2. CHAT TABLE Config
CHAT_TABLE_ID = "chat1"
CHAT_COLS = {
    "input": "User",      # Column where you type
    "output": "AI"        # Column where AI replies
}

# 3. IMAGE TABLE Config
# Make sure your table in JamAI is an "Action Table" using a Vision model (e.g. GPT-4o)
IMAGE_TABLE_ID = "food-analyzer" 
IMAGE_COLS = {
    "image_input": "Image",          # Input column (Type: Image)
    "output_name": "Food Name",      # Output column 1 (Type: Text)
    "output_sugar": "Sugar Content", # Output column 2 (Type: Text/Number)
    "output_risk": "Risk Level"      # Output column 3 (Type: Text)
}

# ==========================================
# 🔌 CLIENT INITIALIZATION
# ==========================================
def init_client():
    """Initializes the JamAI client securely."""
    api_key = st.secrets.get("JAMAI_API_KEY")
    if not api_key:
        st.error("❌ JAMAI_API_KEY missing from secrets.toml")
        return None
    return JamAI(token=api_key, project_id=PROJECT_ID)

# ==========================================
# 💬 LOGIC 1: CHATBOT (FINAL FIX)
# ==========================================
def chat_with_jamai(user_text):
    try:
        client = init_client()
        if not client: return "Error: Connection Failed"

        response = client.table.add_table_rows(
            "chat", 
            p.RowAddRequest(
                table_id=CHAT_TABLE_ID,
                data=[{CHAT_COLS["input"]: user_text}],
                stream=False
            )
        )

        if response and response.rows:
            ai_cell = response.rows[0].columns.get(CHAT_COLS["output"])

            # --- 1. HANDLE "WEIRD" CHAT OBJECT (The Fix) ---
            # This handles: id='chatcmpl-...' choices=[...]
            if hasattr(ai_cell, "choices") and len(ai_cell.choices) > 0:
                # Dig 3 levels deep to find the text
                return ai_cell.choices[0].message.content

            # --- 2. HANDLE STANDARD JAMAI VALUE ---
            if hasattr(ai_cell, "value"):
                return ai_cell.value

            # --- 3. FALLBACK FOR DICTIONARIES ---
            if isinstance(ai_cell, dict) and "value" in ai_cell:
                return ai_cell["value"]

            # --- 4. LAST RESORT ---
            return str(ai_cell)

        return "⚠️ No response from AI."

    except Exception as e:
        return f"❌ Chat Error: {str(e)}"

# ==========================================
# 📸 LOGIC 2: IMAGE ANALYZER
# ==========================================
def analyze_image_with_jamai(uploaded_file):
    """
    Uploads an image to JamAI, sends it to 'food-analyzer' table, 
    and returns specific column data (Name, Sugar, Risk).
    """
    client = init_client()
    if not client: return None

    tmp_path = None
    try:
        # STEP 1: Save Streamlit file to a temp file (JamAI needs a file path on disk)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        # STEP 2: Upload file to JamAI Cloud Storage
        # This returns a URI (e.g., "file://...") that the Table can read
        upload_res = client.file.upload_file(tmp_path)
        image_uri = upload_res.uri

        # STEP 3: Add row to Image Table with the URI
        response = client.table.add_table_rows(
            "action",
            p.RowAddRequest(
                table_id=IMAGE_TABLE_ID,
                data=[{IMAGE_COLS["image_input"]: image_uri}],
                stream=False
            )
        )

        # STEP 4: Parse Results
        if response and response.rows:
            row_data = response.rows[0].columns
            
            # Helper to safely get value from column
            def get_val(col_name):
                item = row_data.get(col_name)
                return item.value if hasattr(item, 'value') else str(item)

            return {
                "food_name": get_val(IMAGE_COLS["output_name"]),
                "sugar": get_val(IMAGE_COLS["output_sugar"]),
                "risk": get_val(IMAGE_COLS["output_risk"])
            }
            
        return None

    except Exception as e:
        st.error(f"❌ Image Analysis Error: {str(e)}")
        return None
        
    finally:
        # Cleanup: Delete the temp file from local server to save space
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)