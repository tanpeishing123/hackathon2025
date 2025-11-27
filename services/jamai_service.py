import streamlit as st
import tempfile
import os
import re
import json
from jamaibase import JamAI, types as p

# ==========================================
# 🔧 CONFIGURATION (MATCH THIS TO YOUR JAMAI TABLES)
# ==========================================

# 1. Project Credentials
PROJECT_ID = st.secrets.get("JAMAI_PROJECT_ID") 

# 2. CHAT TABLE Config
CHAT_TABLE_ID = "chat"
CHAT2_TABLE_ID = "chat2"
CHAT_COLS = {
    "input": "User",      # Column where you type
    "language": "language", # New Language Column
    "output": "AI"        # Column where AI replies
}

# 3. IMAGE TABLE Config
# Make sure your table in JamAI is an "Action Table" using a Vision model (e.g. GPT-4o)
IMAGE_TABLE_ID = "scanner" 
IMAGE_COLS = {
    "image_input": "image",
    "language": "language", # New Language Column
    "output_name": "product_name",
    "output_sugar": "sugar_per_serving",
    "output_fat": "saturated_fat_per_serving",
    "output_sugar_100": "sugar_per_100ml",
    "output_fat_100": "saturated_fat_per_100ml",
    "output_grade": "grade",
    "output_comment": "comment",
    "output_alternative": "alternative", # New Alternative Column
    "output_isBeverage": "isBeverage"
}

# 4. MENU TABLE Config
MENU_TABLE_ID = "menu"
MENU_COLS = {
    "image_input": "menu_image",
    "output_data": "extracted_data"
}

# 5. DRINK TABLE Config
DRINK_TABLE_ID = "drink_scanner"
DRINK_COLS = {
    "image_input": "image",
    "multiplier_input": "multiplier",
    "language": "language", # New Language Column
    "output_name": "product_name",
    "output_isBeverage": "isBeverage",
    "output_sugar": "adjusted_sugar",
    "output_fat": "saturated_fat",
    "output_grade": "grade",
    "output_comment": "Comment",
    "output_alternative": "alternative"
}

# 6. MANUAL INPUT TABLE Config
MANUAL_TABLE_ID = "manual_input"
MANUAL_COLS = {
    "text_input": "text",
    "multiplier_input": "multiplier",
    "language": "language", # New Language Column
    "output_sugar_100": "adjusted_sugar",
    "output_sugar_serving": "adjusted_sugar_per_serving",
    "output_fat_100": "saturated_fat",
    "output_fat_serving": "saturated_fat_per_serving",
    "output_grade": "manual_grade",
    "output_comment": "comment",
    "output_alternative": "alternative"
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
def chat_with_jamai(user_text, table_id="chat", language="English"):
    try:
        client = init_client()
        if not client: return "Error: Connection Failed"

        response = client.table.add_table_rows(
            "chat", 
            p.MultiRowAddRequest(
                table_id=table_id,
                data=[{
                    CHAT_COLS["input"]: user_text,
                    CHAT_COLS["language"]: language
                }],
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

def analyze_image_with_jamai(uploaded_file, language="English"):
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
            p.MultiRowAddRequest(
                table_id=IMAGE_TABLE_ID,
                data=[{
                    IMAGE_COLS["image_input"]: image_uri,
                    IMAGE_COLS["language"]: language
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
            raw_sugar_100 = get_val(IMAGE_COLS["output_sugar_100"])
            raw_fat_100   = get_val(IMAGE_COLS["output_fat_100"])
            raw_grade   = get_val(IMAGE_COLS["output_grade"])
            raw_comment = get_val(IMAGE_COLS["output_comment"])
            raw_alt     = get_val(IMAGE_COLS["output_alternative"])
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
                "sugar_100g": clean_number(raw_sugar_100),
                "fat_100g": clean_number(raw_fat_100),
                "comment": str(raw_comment).strip(),
                "alternative": str(raw_alt).strip(),
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

# ==========================================
# 📜 LOGIC 3: MENU ANALYZER
# ==========================================
# Added menu analysis function
def analyze_menu_with_jamai(uploaded_file):
    """
    Sends menu image to JamAI 'menu' table and returns parsed JSON data.
    """
    # 1. Validation Check
    if not api_key or not PROJECT_ID:
        st.error("❌ Missing API Configuration. Please check your .streamlit/secrets.toml file.")
        return None

    # 2. Initialize JamAI
    jam = JamAI(token=api_key, project_id=PROJECT_ID)

    # 3. Handle File Upload
    temp_filename = f"temp_menu_{uploaded_file.name}"
    with open(temp_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # 4. Upload File to JamAI Storage
        upload_response = jam.file.upload_file(temp_filename)
        image_uri = upload_response.uri

        # 5. Add Row to JamAI Table
        completion = jam.table.add_table_rows(
            "action",
            p.MultiRowAddRequest(
                table_id=MENU_TABLE_ID,
                data=[{
                    MENU_COLS["image_input"]: image_uri
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
            
            # Helper to safely extract content
            def get_val(col_name):
                cell = row.get(col_name)
                if not cell: return "{}"
                if hasattr(cell, "choices") and len(cell.choices) > 0:
                    return cell.choices[0].message.content
                if hasattr(cell, "value"):
                    return cell.value
                return str(cell)

            raw_json = get_val(MENU_COLS["output_data"])
            
            # Clean up JSON string if it contains markdown code blocks
            raw_json = str(raw_json).strip()
            if raw_json.startswith("```json"):
                raw_json = raw_json[7:]
            if raw_json.startswith("```"):
                raw_json = raw_json[3:]
            if raw_json.endswith("```"):
                raw_json = raw_json[:-3]
            
            try:
                parsed_data = json.loads(raw_json)
                return parsed_data
            except json.JSONDecodeError:
                st.error(f"❌ Failed to parse JSON from JamAI. Raw output: {raw_json[:100]}...")
                return None
        else:
            st.error("❌ JamAI returned no rows for menu analysis.")
            return None
            
    except Exception as e:
        st.error(f"❌ Menu Analysis Error: {e}")
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        return None

# ==========================================
# 🍹 LOGIC 4: FRESH DRINK ANALYZER
# ==========================================
def analyze_drink_with_jamai(uploaded_file, multiplier=1.0, language="English"):
    """
    Sends drink image to JamAI 'drink_scanner' table and returns formatted dict.
    """
    # 1. Validation Check
    if not api_key or not PROJECT_ID:
        st.error("❌ Missing API Configuration. Please check your .streamlit/secrets.toml file.")
        return None

    # 2. Initialize JamAI
    jam = JamAI(token=api_key, project_id=PROJECT_ID)

    # 3. Handle File Upload
    temp_filename = f"temp_drink_{uploaded_file.name}"
    with open(temp_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # 4. Upload File to JamAI Storage
        upload_response = jam.file.upload_file(temp_filename)
        image_uri = upload_response.uri

        # 5. Add Row to JamAI Table
        completion = jam.table.add_table_rows(
            "action",
            p.MultiRowAddRequest(
                table_id=DRINK_TABLE_ID,
                data=[{
                    DRINK_COLS["image_input"]: image_uri,
                    DRINK_COLS["multiplier_input"]: multiplier,
                    DRINK_COLS["language"]: language
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
            
            # Helper to safely extract content
            def get_val(col_name):
                cell = row.get(col_name)
                if not cell: return "0"
                if hasattr(cell, "choices") and len(cell.choices) > 0:
                    return cell.choices[0].message.content
                if hasattr(cell, "value"):
                    return cell.value
                return str(cell)

            raw_name    = get_val(DRINK_COLS["output_name"])
            raw_sugar   = get_val(DRINK_COLS["output_sugar"])
            raw_fat     = get_val(DRINK_COLS["output_fat"])
            raw_grade   = get_val(DRINK_COLS["output_grade"])
            raw_is_bev  = get_val(DRINK_COLS["output_isBeverage"]) 
            raw_comment = get_val(DRINK_COLS["output_comment"])
            raw_alt     = get_val(DRINK_COLS["output_alternative"])

            # Logic: Check if it's a beverage
            if isinstance(raw_is_bev, bool):
                is_valid_beverage = raw_is_bev
            else:
                is_valid_beverage = str(raw_is_bev).strip().lower() == 'true'

            sugar_100 = clean_number(raw_sugar)
            fat_100 = clean_number(raw_fat)

            return {
                "name": str(raw_name).strip(),
                "grade": str(raw_grade).strip().upper(),
                "sugar_g": sugar_100 * 2.5,
                "fat_g": fat_100 * 2.5,
                "sugar_100g": sugar_100,
                "fat_100g": fat_100,
                "comment": str(raw_comment).strip(),
                "alternative": str(raw_alt).strip(),
                "is_beverage": is_valid_beverage,
                "serving_text": "(250ml)"
            }
        else:
            st.error("❌ JamAI returned no rows for drink analysis.")
            return None
            
    except Exception as e:
        st.error(f"❌ Drink Analysis Error: {e}")
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        return None

# ==========================================
# ✍️ LOGIC 5: MANUAL INPUT ANALYZER
# ==========================================
def analyze_manual_input_with_jamai(text, multiplier=1.0, language="English"):
    """
    Sends text and multiplier to JamAI 'manual_input' table.
    """
    # 1. Validation Check
    if not api_key or not PROJECT_ID:
        st.error("❌ Missing API Configuration.")
        return None

    # 2. Initialize JamAI
    jam = JamAI(token=api_key, project_id=PROJECT_ID)

    try:
        # 3. Add Row to JamAI Table
        completion = jam.table.add_table_rows(
            "action",
            p.MultiRowAddRequest(
                table_id=MANUAL_TABLE_ID,
                data=[{
                    MANUAL_COLS["text_input"]: text,
                    MANUAL_COLS["multiplier_input"]: multiplier,
                    MANUAL_COLS["language"]: language
                }],
                stream=False
            )
        )

        # 4. Extract Data
        if completion.rows:
            row = completion.rows[0].columns
            
            def get_val(col_name):
                cell = row.get(col_name)
                if not cell: return "0"
                if hasattr(cell, "choices") and len(cell.choices) > 0:
                    return cell.choices[0].message.content
                if hasattr(cell, "value"):
                    return cell.value
                return str(cell)

            # Extract values
            sugar_100 = clean_number(get_val(MANUAL_COLS["output_sugar_100"]))
            sugar_serv = clean_number(get_val(MANUAL_COLS["output_sugar_serving"]))
            fat_100 = clean_number(get_val(MANUAL_COLS["output_fat_100"]))
            fat_serv = clean_number(get_val(MANUAL_COLS["output_fat_serving"]))
            grade = str(get_val(MANUAL_COLS["output_grade"])).strip().upper()
            comment = str(get_val(MANUAL_COLS["output_comment"])).strip()
            alt = str(get_val(MANUAL_COLS["output_alternative"])).strip()

            # If serving values are missing/zero, calculate them (fallback)
            if sugar_serv == 0 and sugar_100 > 0: sugar_serv = sugar_100 * 2.5
            if fat_serv == 0 and fat_100 > 0: fat_serv = fat_100 * 2.5

            return {
                "name": f"{text} (Manual)",
                "grade": grade,
                "sugar_g": sugar_serv,
                "fat_g": fat_serv,
                "sugar_100g": sugar_100,
                "fat_100g": fat_100,
                "comment": comment,
                "alternative": alt,
                "is_beverage": True, # Assume manual input is beverage for now
                "serving_text": "(250ml)" # Standardize for manual input
            }
        else:
            st.error("❌ JamAI returned no rows.")
            return None

    except Exception as e:
        st.error(f"❌ Manual Analysis Error: {e}")
        return None