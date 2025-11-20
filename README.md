# 🌾 Kisan-Dost: AI Crop Doctor

A simple AI-powered web app that helps farmers detect plant diseases using leaf images, explains the illness in **English & Telugu**, recommends **organic and chemical treatments**, and even offers **voice-based remedy playback**. The user can also ask follow-up farming questions using chat.

---

## What It Does

| Feature              | Description                                 |
| -------------------- | ------------------------------------------- |
| 📸 Upload Leaf Image | Detects disease using Gemini Vision         |
| 🧠 Diagnosis         | Identifies disease name + confidence level  |
| 🌐 Bilingual Output  | English + Telugu remedies and explanation   |
| 🔊 Voice Support     | Telugu audio playback of remedy             |
| 💬 AI Follow-up Chat | Asks questions like “Can I spray it daily?” |
| 📊 Analytics         | Shows most detected diseases from Firestore |

---

##  System Flow

```
User (Browser)
   ↓
Streamlit App on Cloud Run
   ↓
Gemini-2.5-Flash Vision → Detect disease from image
   ↓
Gemini Text LLM → Generate bilingual explanation + remedies
   ↓
Firestore → Store diagnosis
   ↓
Streamlit UI → Display results, play audio, show charts and ask follow-up questions
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repo and install dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ **Update your Project ID in `app.py`**

🔹 Replace this line with your GCP Project ID:

```python
PROJECT_ID = "build-blog-hyd-478805"
```

### 3️⃣ Enable Google Cloud authentication

```bash
gcloud auth login
```

### 4️⃣ Run locally for testing

```bash
streamlit run app.py
```

👉 Open in browser at: `http://localhost:8501`

---

## 🚀 Deployment to Cloud Run
🔹 navigate to the kisam-dost directory then run the following command

```bash
gcloud run deploy kisan-dost \
  --image gcr.io/build-blog-hyd-478805/kisan-dost \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated
```

---

## 💾 Firestore Sample Record

```json
{
  "is_plant": true,
  "disease_name": "Soybean Rust",
  "confidence": 0.98,
  "english": {
    "explanation": "Soybean Rust, caused by the fungus Phakopsora pachyrhizi...",
    "organic_remedy": "For early stages, spray 3-5% Neem oil solution...",
    "chemical_remedy": "Apply Propiconazole 25% EC (1 ml/liter), Tebuconazole 25% EC..."
  },
  "telugu": {
    "disease_name": "సోయాబీన్ రస్ట్ (కుంకుమ తెగులు)",
    "explanation": "సోయాబీన్ రస్ట్ అనేది ఫాకోప్సోరా పచిరిజి అనే శిలీంద్రం వల్ల...",
    "organic_remedy": "3-5% వేప నూనె ద్రావణాన్ని 7-10 రోజుల వ్యవధిలో పిచికారీ చేయాలి...",
    "chemical_remedy": "ప్రొపికోనజోల్, టెబుకోనజోల్, అజాక్సిస్ట్రోబిన్ మందులను 1 మి.లీ/లీటర్ పిచికారీ చేయాలి..."
  },
  "timestamp": "2025-11-20T16:58:58.138+05:30"
}
```

---

## 🛠 Tech Used

| Component          | Technology                     |
| ------------------ | ------------------------------ |
| Frontend + Backend | Streamlit                      |
| Hosting            | Cloud Run                      |
| AI Services        | Gemini-2.5-Flash Vision & Text |
| Database           | Firestore        |
| Voice              | gTTS       |
| Language           | English + Telugu               |

---

## 👨‍🌾 Built By

**Hari Thatikonda,**
**Nikhil Gattu**

---

> 🌱 “Bringing AI to the field”

