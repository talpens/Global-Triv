import streamlit as st
import google.generativeai as genai
import json

# 1. הגדרות API ודגם (החלף את YOUR_API_KEY במפתח שלך)
genai.configure(api_key="AIzaSyBVNZGeegSIzRiR-LSisj_M7jO_u5UZTag")
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# 2. עיצוב הממשק (סטייל רטרו/חלל)
st.set_page_config(page_title="טריוויה גלובלית ומקומית", layout="centered")
st.markdown("""
    <style>
    body { background-color: #0e1117; color: white; }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3.5em; 
        background-color: #1f2937; color: #fbbf24; 
        border: 2px solid #fbbf24; font-weight: bold;
        font-family: 'Courier New', Courier, monospace;
    }
    .stButton>button:hover { background-color: #fbbf24; color: #1f2937; }
    .score-box { padding: 10px; border: 1px solid #4b5563; border-radius: 5px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 3. ניהול מצב המשחק (Session State)
if 'page' not in st.session_state:
    st.session_state.page = "welcome"
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0
if 'current_q' not in st.session_state:
    st.session_state.current_q = None

# --- פונקציות לוגיקה ---

def get_question_from_ai():
    """מושך שאלה בפורמט JSON מה-API של גוגל"""
    prompt = """
    צור שאלה אחת למשחק טריוויה על דגלי מדינות. 
    החזר אך ורק פורמט JSON תקני כזה:
    {"question": "שם המדינה", "options": ["א", "ב", "ג", "ד"], "answer": "התשובה הנכונה"}
    הקפד שהתשובה הנכונה תהיה אחת מהאופציות ושכל הטקסט יהיה בעברית.
    """
    response = model.generate_content(prompt)
    try:
        # ניקוי הטקסט למקרה שהמודל מוסיף תגיות ```json
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except:
        return {"question": "ישראל", "options": ["ישראל", "צרפת", "יוון", "יפן"], "answer": "ישראל"}

# --- דפי המשחק ---

# דף 1: מסך פתיחה ורישום
if st.session_state.page == "welcome":
    st.image("logo.png") # וודא שהקובץ בתיקיה
    st.write("---")
    st.subheader("הזן שם כדי להיכנס לטבלת השיאים:")
    name_input = st.text_input("שם השחקן:", placeholder="למשל: טל")
    
    if st.button("בוא נשחק!"):
        if name_input:
            st.session_state.user_name = name_input
            st.session_state.page = "game"
            st.session_state.current_q = get_question_from_ai()
            st.rerun()
        else:
            st.warning("חובה להזין שם כדי להתחיל")

# דף 2: מהלך המשחק
elif st.session_state.page == "game":
    st.sidebar.markdown(f"### שחקן: {st.session_state.user_name}")
    st.sidebar.markdown(f"### ניקוד: {st.session_state.score}")
    
    q = st.session_state.current_q
    st.title("זהה את המדינה!")
    st.info(f"שאלה על המדינה: **{q['question']}**") # כאן בהמשך נוסיף לינק לתמונה של הדגל
    
    # הצגת כפתורי תשובה
    cols = st.columns(2)
    for i, option in enumerate(q['options']):
        with cols[i % 2]:
            if st.button(option):
                if option == q['answer']:
                    st.success("נכון מאוד! 🎉")
                    st.session_state.score += 1
                else:
                    st.error(f"טעות... התשובה הנכונה הייתה {q['answer']}")
                
                st.session_state.total_questions += 1
                # טעינת שאלה חדשה
                st.session_state.current_q = get_question_from_ai()
                st.button("לשאלה הבאה ➡️")

    if st.sidebar.button("סיים משחק"):
        st.session_state.page = "summary"
        st.rerun()

# דף 3: סיכום
elif st.session_state.page == "summary":
    st.balloons()
    st.title("המשחק נגמר!")
    st.header(f"{st.session_state.user_name}, צברת {st.session_state.score} נקודות!")
    if st.button("חזרה למסך הראשי"):
        st.session_state.page = "welcome"
        st.session_state.score = 0
        st.rerun()
