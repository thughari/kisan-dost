import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import firestore
import datetime
import json
import pandas as pd
from gtts import gTTS
from io import BytesIO

PROJECT_ID = "build-blog-hyd-478805" 
LOCATION = "europe-west1"

st.set_page_config(page_title="Kisan-Dost", page_icon="🌾", layout="wide")

@st.cache_resource
def init_services():
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = GenerativeModel("gemini-2.5-flash-lite") 
        db = firestore.Client(project=PROJECT_ID)
        return model, db
    except Exception as e:
        st.error(f"Error initializing Cloud Services: {e}")
        return None, None

model, db = init_services()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_diagnosis" not in st.session_state:
    st.session_state.last_diagnosis = None

def reset_state():
    st.session_state.last_diagnosis = None
    st.session_state.messages = []

def text_to_audio(text, lang='te'):
    try:
        tts = gTTS(text=text, lang=lang)
        fp = BytesIO()
        tts.write_to_fp(fp)
        return fp
    except Exception as e:
        return None

def analyze_image(image_bytes):
    image_part = Part.from_data(data=image_bytes, mime_type="image/jpeg")
    
    prompt = """
    You are an expert Agricultural Scientist in India. 
    
    STEP 1: VALIDATION
    Check if this image contains a crop, plant, or leaf. 
    If it is NOT a plant (e.g., a face, a car, a building), return JSON: {"is_plant": false}
    
    STEP 2: ANALYSIS (Only if it is a plant)
    1. Identify the disease or pest. 
       IMPORTANT: Use the standard, short English common name (e.g., "Early Blight", "Leaf Curl Virus", "Powdery Mildew"). 
       Do not use long descriptions in the name field.
    2. Recommend a specific ORGANIC remedy available in India.
    3. Recommend a specific CHEMICAL remedy if severe.
    4. Translate the diagnosis and remedies into simple TELUGU.
    5. Provide a confidence score (0.0 to 1.0).
    
    OUTPUT FORMAT:
    Strictly output valid JSON only. Structure:
    {
        "is_plant": true,
        "disease_name": "Standardized Name",
        "confidence": 0.95, 
        "english": {
            "explanation": "Brief explanation",
            "organic_remedy": "...",
            "chemical_remedy": "..."
        },
        "telugu": {
            "disease_name": "Name in Telugu",
            "explanation": "Explanation in Telugu",
            "organic_remedy": "...",
            "chemical_remedy": "..."
        }
    }
    """
    
    responses = model.generate_content(
        [image_part, prompt],
        generation_config={
            "response_mime_type": "application/json",
            "temperature": 0.0
        }
    )
    return json.loads(responses.text)

def ask_followup(question, context):
    chat_model = GenerativeModel("gemini-2.5-flash-lite")
    prompt = f"""
    Context: Plant disease '{context['disease_name']}'. Remedy: '{context['english']['organic_remedy']}'.
    User Q: {question}
    Answer simply and kindly in English (with a Telugu translation in brackets).
    Keep it short (under 50 words).
    """
    response = chat_model.generate_content(prompt)
    return response.text

def save_to_firestore(data):
    if db:
        collection_ref = db.collection("diagnoses")
        log_data = data.copy()
        log_data["timestamp"] = datetime.datetime.now()
        collection_ref.add(log_data)


st.title("🌾 Kisan-Dost: AI Crop Doctor")
st.markdown("### Telangana's First AI Assistant for Farmers")

st.sidebar.header("📊 Disease Dashboard")
if st.sidebar.button("Update Analytics"):
    st.toast("Analytics Updated!")

try:
    docs = db.collection("diagnoses").stream()
    data_list = [doc.to_dict() for doc in docs]
    
    if data_list:
        df = pd.DataFrame(data_list)
        if 'disease_name' in df.columns:
            clean_df = df.dropna(subset=['disease_name'])
            clean_df = clean_df[clean_df['disease_name'] != ""]
            clean_df = clean_df[~clean_df['disease_name'].astype(str).str.contains("Unknown", case=False)]
            
            if not clean_df.empty:
                counts = clean_df['disease_name'].value_counts().head(5)
                st.sidebar.subheader("Top 5 Detected Diseases")
                st.sidebar.bar_chart(counts)
            else:
                st.sidebar.info("No valid disease data yet.")
        else:
            st.sidebar.warning("Not enough data yet.")
    else:
        st.sidebar.info("No data in database yet.")
except Exception as e:
    st.sidebar.error(f"Could not load analytics: {e}")


uploaded_file = st.file_uploader(
    "📸 Upload a leaf photo / ఆకు ఫోటోను అప్‌లోడ్ చేయండి", 
    type=["jpg", "jpeg", "png"],
    on_change=reset_state
)

image_to_analyze = None
start_analysis = False

if uploaded_file is not None:
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        if st.button("🏥 Analyze Uploaded Photo", type="primary"):
            image_to_analyze = uploaded_file.getvalue()
            start_analysis = True

else:
    st.markdown("---")
    st.markdown("#### ⚡ Quick Demo (Tap an image to analyze instantly)")

    sample_images = {
        "sample 1": "assets/sample1.jpg",
        "sample 2": "assets/sample2.jpg",
        "sample 3": "assets/sample3.jpg"
    }

    d1, d2, d3 = st.columns(3)
    cols = [d1, d2, d3]

    for col, (name, path) in zip(cols, sample_images.items()):
        with col:
            try:
                st.image(path, caption=name, use_container_width=True)
                if st.button(f"Analyze {name}", key=name):
                    with open(path, "rb") as f:
                        image_to_analyze = f.read()
                    start_analysis = True
                    reset_state()
            except FileNotFoundError:
                st.error(f"Missing file: {path}")


if start_analysis and image_to_analyze:
    with st.spinner("AI Doctor is checking the leaf..."):
        try:
            data = analyze_image(image_to_analyze)
            
            if data.get("is_plant") is False:
                st.error("⚠️ Error: This does not look like a plant leaf. Please upload a clear photo of a crop.")
            else:
                save_to_firestore(data)
                st.session_state.last_diagnosis = data
                st.session_state.messages = []
        except Exception as e:
            st.error("Oops! The AI got confused. Please try again.")
            st.error(f"Debug Error: {e}")

if st.session_state.last_diagnosis:
    data = st.session_state.last_diagnosis
    
    st.success(f"**Detected:** {data['disease_name']} (Confidence: {data['confidence']})")
    
    tab_en, tab_te = st.tabs(["🇬🇧 English Report", "🇮🇳 Telugu Report"])
    
    with tab_en:
        st.subheader("Diagnosis")
        st.write(data['english']['explanation'])
        st.subheader("💊 Remedies")
        st.info(f"**Organic:** {data['english']['organic_remedy']}")
        st.warning(f"**Chemical:** {data['english']['chemical_remedy']}")
        
    with tab_te:
        st.subheader(f"వ్యాధి: {data['telugu']['disease_name']}")
        st.write(data['telugu']['explanation'])
        
        st.subheader("🔊 Listen")
        audio_text = f"{data['telugu']['disease_name']}. {data['telugu']['organic_remedy']}"
        audio_bytes = text_to_audio(audio_text, lang='te')
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
        
        st.subheader("💊 నివారణలు")
        st.info(f"**సేంద్రీయ:** {data['telugu']['organic_remedy']}")
        st.warning(f"**రసాయన:** {data['telugu']['chemical_remedy']}")

if st.session_state.last_diagnosis:
    st.markdown("---")
    st.subheader("💬 Ask the AI Doctor (Questions?)")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question (e.g., 'Can I spray this daily?')"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ask_followup(prompt, st.session_state.last_diagnosis)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})