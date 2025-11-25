import streamlit as st
import tempfile
import os
import re
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
IMAGE_TABLE_ID = "scanner" 
IMAGE_COLS = {
    "image_input": "image",
    "output_name": "product_name",
    "output_sugar": "sugar_per_serving",
    "output_fat": "saturated_fat_per_serving",
    "output_grade": "grade",
    "output_comment": "comment",
    "output_isBeverage": "isBeverage"
}
api_key = st.secrets.get("JAMAI_API_KEY")
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
def clean_number(value):
    """
    Helper: Extracts the first number from a string.
    e.g., "12.5g" -> 12.5, "approx 4 grams" -> 4.0
    """
    if not value:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
        
    # Regex to find integer or decimal numbers
    match = re.search(r"(\d+(\.\d+)?)", str(value))
    if match:
        return float(match.group(1))
    return 0.0

def analyze_image_with_jamai(uploaded_file):
    """
    Sends image to JamAI Base table and returns formatted dict for UI.
    """
    # 1. Validation Check
    if not api_key or not PROJECT_ID:
        st.error("❌ Missing API Configuration. Please check your .streamlit/secrets.toml file.")
        return None

    # 2. Initialize JamAI
    jam = JamAI(token=api_key, project_id=PROJECT_ID)

    # 3. Handle File Upload
    temp_filename = f"temp_{uploaded_file.name}"
    with open(temp_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # 4. Upload File to JamAI Storage
        upload_response = jam.file.upload_file(temp_filename)
        image_uri = upload_response.uri

        # 5. Add Row to JamAI Table
        # Using add_table_rows with the correct protocol
        completion = jam.table.add_table_rows(
            "action",
            p.RowAddRequest(
                table_id=IMAGE_TABLE_ID,
                data=[{
                    IMAGE_COLS["image_input"]: image_uri
                }],
                stream=False
            )
        )

        # 6. Clean up temp file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        # 7. Extract Data from Response
        if completion.rows:
            row = completion.rows[0].columns
            
            # Helper to safely extract content from mixed cell types
            def get_val(col_name):
                cell = row.get(col_name)
                if not cell: return "0"
                # Check for ChatCompletion object
                if hasattr(cell, "choices") and len(cell.choices) > 0:
                    return cell.choices[0].message.content
                # Check for standard value attribute
                if hasattr(cell, "value"):
                    return cell.value
                # Fallback
                return str(cell)

            raw_name    = get_val(IMAGE_COLS["output_name"])
            raw_sugar   = get_val(IMAGE_COLS["output_sugar"])
            raw_fat     = get_val(IMAGE_COLS["output_fat"])
            raw_grade   = get_val(IMAGE_COLS["output_grade"])
            raw_comment = get_val(IMAGE_COLS["output_comment"])
            raw_is_bev  = get_val(IMAGE_COLS["output_isBeverage"]) 

            # Logic: Check if it's a beverage
            if isinstance(raw_is_bev, bool):
                is_valid_beverage = raw_is_bev
            else:
                is_valid_beverage = str(raw_is_bev).strip().lower() == 'true'

            return {
                "name": str(raw_name).strip(),
                "grade": str(raw_grade).strip().upper(),
                "sugar_g": clean_number(raw_sugar),
                "fat_g": clean_number(raw_fat),
                "comment": str(raw_comment).strip(),
                "is_beverage": is_valid_beverage
            }
        else:
            st.error("❌ JamAI returned no rows. Check if your table has Flow enabled.")
            return None
            
    except Exception as e:
        st.error(f"❌ Image Analysis Error: {e}")
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        return None