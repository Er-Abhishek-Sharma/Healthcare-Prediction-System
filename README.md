# 🏥 HealthPredict AI — Healthcare Disease Prediction System
### Final Year Major Project | Django + Machine Learning

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3-orange)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)

---

## 📋 Project Overview

HealthPredict AI is a full-stack web application that uses Machine Learning to predict diseases based on patient-reported symptoms. Built as a Final Year Major Project, it demonstrates the integration of Django backend, scikit-learn ML models, and a responsive Bootstrap frontend.

---

## 🎯 Features

| Feature | Description |
|---|---|
| 🔐 Authentication | Role-based login (Patient / Doctor / Admin) |
| 🤖 ML Prediction | 4 algorithms with accuracy comparison |
| 📊 Charts | Chart.js visualizations for results & trends |
| 📄 PDF Reports | Downloadable prediction reports via ReportLab |
| 📧 Email | Send reports to patient email |
| 👨‍⚕️ Doctor Finder | Browse specialists by disease |
| 🔍 History Search | Full medical history with search |
| 🛡️ Admin Panel | Django admin for full data management |

---

## 🧠 Machine Learning Models

| Algorithm | Typical Accuracy |
|---|---|
| Random Forest | ~95% |
| Decision Tree | ~90% |
| SVM (RBF kernel) | ~88% |
| Naive Bayes | ~85% |

- **Dataset**: 132 symptoms → 41 diseases
- **Training**: 80/20 train-test split + 5-fold cross-validation
- **Best model auto-selected** and saved with pickle

---

## 📁 Project Structure

```
healthcare_prediction/
│
├── manage.py
├── requirements.txt
├── Procfile                    # Heroku deployment
├── runtime.txt
│
├── healthcare_project/         # Django project config
│   ├── settings.py
│   ├── settings_production.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/                   # User auth app
│   ├── models.py               # Custom User model
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── patients/                   # Patient data app
│   ├── models.py               # PatientProfile, Disease, Symptom, DoctorProfile
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── predictions/                # ML prediction app
│   ├── models.py               # Prediction, PredictionSymptom
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── management/
│       └── commands/
│           ├── train_models.py # python manage.py train_models
│           └── seed_data.py    # python manage.py seed_data
│
├── ml_module/                  # Machine Learning engine
│   ├── predictor.py            # Core ML engine (train, predict, compare)
│   ├── trained_models/         # Saved .pkl model files (auto-generated)
│   └── data/                   # Dataset CSV files
│
├── templates/                  # HTML templates
│   ├── base/
│   │   ├── base.html           # Main layout with sidebar
│   │   └── home.html           # Landing page
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register_patient.html
│   │   ├── register_doctor.html
│   │   └── profile.html
│   ├── patients/
│   │   ├── dashboard.html
│   │   ├── doctor_list.html
│   │   └── medical_history.html
│   └── predictions/
│       ├── predict.html        # Symptom selection
│       ├── result.html         # Prediction results + charts
│       ├── history.html
│       └── doctor_dashboard.html
│
└── static/                     # CSS, JS, Images
```

---

## ⚡ Quick Setup (Local Development)

### Step 1 — Clone and Setup Virtual Environment
```bash
git clone <your-repo-url>
cd healthcare_prediction

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Configure Settings
```bash
# In healthcare_project/settings.py:
# - Set SECRET_KEY (change the default)
# - Configure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD for email features
```

### Step 4 — Database Setup
```bash
python manage.py makemigrations accounts
python manage.py makemigrations patients
python manage.py makemigrations predictions
python manage.py migrate
```

### Step 5 — Seed Initial Data
```bash
# Populates symptoms and disease data in the database
python manage.py seed_data
```

### Step 6 — Train ML Models
```bash
# Uses synthetic data by default (no dataset needed)
python manage.py train_models

# Or with a real dataset from Kaggle:
# https://www.kaggle.com/datasets/itachi9604/disease-symptom-description-dataset
python manage.py train_models --dataset ml_module/data/dataset.csv
```

### Step 7 — Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### Step 8 — Run the Server
```bash
python manage.py runserver
```

### Step 9 — Open in Browser
```
http://127.0.0.1:8000/          → Home page
http://127.0.0.1:8000/admin/    → Django admin panel
http://127.0.0.1:8000/accounts/login/      → Login
http://127.0.0.1:8000/accounts/register/patient/  → Register
http://127.0.0.1:8000/predictions/predict/         → Predict disease
```

---

## 🗄️ Using a Real Dataset

Download the Disease Symptom Prediction dataset from Kaggle:
```
https://www.kaggle.com/datasets/itachi9604/disease-symptom-description-dataset
```

Place `dataset.csv` in `ml_module/data/` then run:
```bash
python manage.py train_models --dataset ml_module/data/dataset.csv
```

The dataset has columns: `Symptom_1` through `Symptom_17`, `prognosis`

---

## 🚀 Deployment on Render (Free Tier)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/healthcare-prediction.git
git push -u origin main
```

### Step 2 — Create Render Web Service
1. Go to https://render.com → New → Web Service
2. Connect your GitHub repository
3. Set:
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
   - **Start Command**: `gunicorn healthcare_project.wsgi`

### Step 3 — Set Environment Variables on Render
```
DJANGO_SETTINGS_MODULE = healthcare_project.settings_production
SECRET_KEY = your-very-secret-key-here
DATABASE_URL = postgres://... (Render provides this)
ALLOWED_HOSTS = your-app.onrender.com
EMAIL_HOST_USER = your-gmail@gmail.com
EMAIL_HOST_PASSWORD = your-gmail-app-password
```

### Step 4 — After Deployment
```bash
# Run via Render Shell:
python manage.py seed_data
python manage.py train_models
python manage.py createsuperuser
```

---

## 🚀 Deployment on Heroku

```bash
# Install Heroku CLI then:
heroku create healthcare-prediction-app
heroku addons:create heroku-postgresql:mini
heroku config:set DJANGO_SETTINGS_MODULE=healthcare_project.settings_production
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py seed_data
heroku run python manage.py train_models
heroku run python manage.py createsuperuser
```

---

## 📧 Email Setup (Gmail)

1. Enable 2-Factor Authentication on Gmail
2. Go to Google Account → Security → App Passwords
3. Generate an App Password for "Mail"
4. Use it as `EMAIL_HOST_PASSWORD` in settings

---

## 🔬 ML Module Internals

```python
from ml_module.predictor import get_prediction_engine

engine = get_prediction_engine()

# Predict from a list of symptoms
result = engine.predict(['headache', 'high_fever', 'nausea', 'vomiting'])
print(result)
# {
#   'predicted_disease': 'Malaria',
#   'confidence': 0.87,
#   'confidence_percentage': '87.0%',
#   'top_predictions': [...],
#   'model_used': 'Random Forest'
# }

# Compare all models
comparison = engine.compare_all_models(['headache', 'fever'])

# Get accuracy summary
accuracy = engine.get_accuracy_summary()
```

---

## 📊 Database Models

```
User (Custom AbstractUser)
  ├── role: patient | doctor | admin
  ├── phone, dob, gender, address
  └── doctor fields: specialization, license_number, hospital_name

PatientProfile (OneToOne → User)
  ├── blood_group, height, weight
  ├── allergies, chronic_conditions
  └── emergency_contact

Disease
  ├── name, description, category, icd_code
  ├── precautions, medications, diet_plan
  ├── risk_level: low | medium | high | critical
  └── recommended_specialist

Symptom
  └── name, description, severity_weight

Prediction
  ├── patient (FK → User)
  ├── symptoms (M2M via PredictionSymptom)
  ├── predicted_disease (FK → Disease)
  ├── confidence_score, model_used
  └── algorithm_results (JSONField)
```

---

## 🎓 Project Report Outline

1. **Introduction** — Healthcare + AI, problem motivation
2. **Problem Statement** — Manual diagnosis limitations
3. **System Architecture** — Django MVT + ML pipeline diagram
4. **Methodology** — Dataset, preprocessing, training, evaluation
5. **Results & Accuracy** — Model comparison table + charts
6. **Conclusion** — Achievements, limitations, future scope

### Future Scope Ideas:
- Deep learning (CNN/LSTM) for more complex patterns
- Integration with wearable devices (heart rate, SpO2)
- Real-time doctor video consultation
- Mobile app (Flutter/React Native)
- NLP symptom input (type symptoms naturally)
- Multilingual support

---

## ⚠️ Disclaimer

This system is built **for educational and research purposes only**. The predictions made by this AI system should **never replace professional medical advice**. Always consult a qualified healthcare professional for diagnosis and treatment.

---

## 👨‍💻 Built With

- **Backend**: Django 4.2, Python 3.11
- **ML**: scikit-learn, pandas, numpy
- **Frontend**: Bootstrap 5.3, Chart.js, Bootstrap Icons
- **PDF**: ReportLab
- **DB**: SQLite (dev) / PostgreSQL (prod)
- **Auth**: Django built-in auth + custom User model

---

*Healthcare Prediction System — Final Year Major Project*
