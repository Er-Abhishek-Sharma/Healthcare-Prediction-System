"""
ML Module - Healthcare Disease Prediction Engine
=================================================
Implements multiple ML algorithms for disease prediction:
1. Decision Tree Classifier
2. Random Forest Classifier
3. Naive Bayes Classifier
4. Support Vector Machine (SVM)

Trains, evaluates, compares, and saves the best model.
"""

import os
import pickle
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

logger = logging.getLogger(__name__)

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / 'trained_models'
DATA_DIR = BASE_DIR / 'data'
MODELS_DIR.mkdir(exist_ok=True)


# ─── Symptom List (132 symptoms matching standard healthcare datasets) ─────────
SYMPTOM_LIST = [
    'itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing', 'shivering',
    'chills', 'joint_pain', 'stomach_pain', 'acidity', 'ulcers_on_tongue',
    'muscle_wasting', 'vomiting', 'burning_micturition', 'spotting_urination', 'fatigue',
    'weight_gain', 'anxiety', 'cold_hands_and_feets', 'mood_swings', 'weight_loss',
    'restlessness', 'lethargy', 'patches_in_throat', 'irregular_sugar_level', 'cough',
    'high_fever', 'sunken_eyes', 'breathlessness', 'sweating', 'dehydration',
    'indigestion', 'headache', 'yellowish_skin', 'dark_urine', 'nausea',
    'loss_of_appetite', 'pain_behind_the_eyes', 'back_pain', 'constipation', 'abdominal_pain',
    'diarrhoea', 'mild_fever', 'yellow_urine', 'yellowing_of_eyes', 'acute_liver_failure',
    'fluid_overload', 'swelling_of_stomach', 'swelled_lymph_nodes', 'malaise', 'blurred_and_distorted_vision',
    'phlegm', 'throat_irritation', 'redness_of_eyes', 'sinus_pressure', 'runny_nose',
    'congestion', 'chest_pain', 'weakness_in_limbs', 'fast_heart_rate', 'pain_during_bowel_movements',
    'pain_in_anal_region', 'bloody_stool', 'irritation_in_anus', 'neck_pain', 'dizziness',
    'cramps', 'bruising', 'obesity', 'swollen_legs', 'swollen_blood_vessels',
    'puffy_face_and_eyes', 'enlarged_thyroid', 'brittle_nails', 'swollen_extremeties', 'excessive_hunger',
    'extra_marital_contacts', 'drying_and_tingling_lips', 'slurred_speech', 'knee_pain', 'hip_joint_pain',
    'muscle_weakness', 'stiff_neck', 'swelling_joints', 'movement_stiffness', 'spinning_movements',
    'loss_of_balance', 'unsteadiness', 'weakness_of_one_body_side', 'loss_of_smell', 'bladder_discomfort',
    'foul_smell_ofurine', 'continuous_feel_of_urine', 'passage_of_gases', 'internal_itching', 'toxic_look_(typhos)',
    'depression', 'irritability', 'muscle_pain', 'altered_sensorium', 'red_spots_over_body',
    'belly_pain', 'abnormal_menstruation', 'dischromic_patches', 'watering_from_eyes', 'increased_appetite',
    'polyuria', 'family_history', 'mucoid_sputum', 'rusty_sputum', 'lack_of_concentration',
    'visual_disturbances', 'receiving_blood_transfusion', 'receiving_unsterile_injections', 'coma', 'stomach_bleeding',
    'distention_of_abdomen', 'history_of_alcohol_consumption', 'fluid_overload.1', 'blood_in_sputum',
    'prominent_veins_on_calf', 'palpitations', 'painful_walking', 'pus_filled_pimples', 'blackheads',
    'scurring', 'skin_peeling', 'silver_like_dusting', 'small_dents_in_nails', 'inflammatory_nails',
    'blister', 'red_sore_around_nose', 'yellow_crust_ooze',
]

DISEASE_LIST = [
    'Fungal infection', 'Allergy', 'GERD', 'Chronic cholestasis', 'Drug Reaction',
    'Peptic ulcer diseae', 'AIDS', 'Diabetes', 'Gastroenteritis', 'Bronchial Asthma',
    'Hypertension', 'Migraine', 'Cervical spondylosis', 'Paralysis (brain hemorrhage)',
    'Jaundice', 'Malaria', 'Chicken pox', 'Dengue', 'Typhoid', 'hepatitis A',
    'Hepatitis B', 'Hepatitis C', 'Hepatitis D', 'Hepatitis E', 'Alcoholic hepatitis',
    'Tuberculosis', 'Common Cold', 'Pneumonia', 'Dimorphic hemmorhoids(piles)',
    'Heart attack', 'Varicose veins', 'Hypothyroidism', 'Hyperthyroidism',
    'Hypoglycemia', 'Osteoarthritis', 'Arthritis',
    '(vertigo) Paroymsal  Positional Vertigo', 'Acne', 'Urinary tract infection',
    'Psoriasis', 'Impetigo',
]


def generate_dummy_dataset(n_samples=5000):
    """
    Generate a synthetic healthcare dataset for demonstration.
    In production, use the real Kaggle disease-symptom dataset.

    Dataset structure:
    - 132 symptom columns (0 or 1)
    - 1 disease label column
    """
    np.random.seed(42)

    # Symptom-disease mapping (each disease has 3-7 primary symptoms)
    disease_symptom_map = {
        'Fungal infection': ['itching', 'skin_rash', 'nodal_skin_eruptions', 'dischromic_patches'],
        'Allergy': ['continuous_sneezing', 'shivering', 'chills', 'watering_from_eyes', 'runny_nose'],
        'GERD': ['stomach_pain', 'acidity', 'ulcers_on_tongue', 'vomiting', 'cough'],
        'Diabetes': ['fatigue', 'weight_loss', 'restlessness', 'lethargy', 'irregular_sugar_level',
                     'blurred_and_distorted_vision', 'obesity', 'excessive_hunger', 'polyuria'],
        'Hypertension': ['headache', 'chest_pain', 'dizziness', 'loss_of_balance', 'nausea'],
        'Migraine': ['headache', 'blurred_and_distorted_vision', 'nausea', 'vomiting', 'fatigue'],
        'Common Cold': ['continuous_sneezing', 'cough', 'runny_nose', 'congestion', 'mild_fever'],
        'Typhoid': ['high_fever', 'headache', 'vomiting', 'nausea', 'constipation', 'abdominal_pain'],
        'Malaria': ['chills', 'high_fever', 'sweating', 'headache', 'nausea', 'vomiting', 'fatigue'],
        'Dengue': ['high_fever', 'headache', 'pain_behind_the_eyes', 'joint_pain', 'skin_rash', 'nausea'],
        'Pneumonia': ['cough', 'high_fever', 'breathlessness', 'chest_pain', 'fatigue', 'phlegm'],
        'Bronchial Asthma': ['breathlessness', 'cough', 'wheezing', 'fatigue', 'chest_pain'],
        'Heart attack': ['chest_pain', 'breathlessness', 'sweating', 'nausea', 'vomiting', 'fatigue'],
        'Jaundice': ['yellowish_skin', 'dark_urine', 'nausea', 'loss_of_appetite', 'fatigue'],
        'Tuberculosis': ['cough', 'blood_in_sputum', 'high_fever', 'weight_loss', 'fatigue', 'breathlessness'],
        'AIDS': ['muscle_wasting', 'fatigue', 'high_fever', 'swelled_lymph_nodes', 'weight_loss'],
        'Acne': ['skin_rash', 'pus_filled_pimples', 'blackheads', 'scurring'],
        'Urinary tract infection': ['burning_micturition', 'bladder_discomfort', 'foul_smell_ofurine',
                                    'continuous_feel_of_urine'],
        'Psoriasis': ['skin_rash', 'joint_pain', 'skin_peeling', 'silver_like_dusting', 'small_dents_in_nails'],
        'Gastroenteritis': ['vomiting', 'diarrhoea', 'abdominal_pain', 'nausea', 'dehydration'],
    }

    records = []
    diseases_used = list(disease_symptom_map.keys())

    for _ in range(n_samples):
        disease = np.random.choice(diseases_used)
        primary_symptoms = disease_symptom_map.get(disease, [])

        row = {s: 0 for s in SYMPTOM_LIST}

        # Add primary symptoms with high probability
        for symptom in primary_symptoms:
            if symptom in row:
                row[symptom] = 1 if np.random.random() > 0.15 else 0

        # Add random noise symptoms with low probability
        noise_symptoms = np.random.choice(SYMPTOM_LIST, size=np.random.randint(0, 4), replace=False)
        for s in noise_symptoms:
            row[s] = 1

        row['prognosis'] = disease
        records.append(row)

    df = pd.DataFrame(records)
    return df


class HealthcarePredictionEngine:
    """
    Core ML engine for disease prediction.
    Trains multiple models, compares accuracy, and uses the best one.
    """

    def __init__(self):
        self.models = {
            'Decision Tree': DecisionTreeClassifier(
                max_depth=10,
                min_samples_split=5,
                random_state=42
            ),
            'Random Forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=12,
                random_state=42,
                n_jobs=-1
            ),
            'Naive Bayes': GaussianNB(),
            'SVM': SVC(
                kernel='rbf',
                probability=True,
                random_state=42
            ),
        }
        self.best_model = None
        self.best_model_name = None
        self.label_encoder = LabelEncoder()
        self.accuracy_results = {}
        self.feature_names = SYMPTOM_LIST

    def load_data(self, csv_path=None):
        """
        Load dataset. If no path provided, generates dummy data.
        For production: Download from Kaggle - 'Disease Symptom Prediction'
        URL: https://www.kaggle.com/datasets/itachi9604/disease-symptom-description-dataset
        """
        if csv_path and os.path.exists(csv_path):
            logger.info(f"Loading dataset from {csv_path}")
            df = pd.read_csv(csv_path)
        else:
            logger.info("Generating synthetic dataset for demonstration")
            df = generate_dummy_dataset(n_samples=5000)

        return df

    def preprocess_data(self, df):
        """
        Preprocess the dataset:
        - Extract features (symptoms) and target (disease)
        - Encode disease labels
        - Handle missing values
        """
        # Identify symptom columns
        symptom_cols = [col for col in df.columns if col in SYMPTOM_LIST]

        # Ensure all symptom columns exist
        for col in SYMPTOM_LIST:
            if col not in df.columns:
                df[col] = 0

        X = df[SYMPTOM_LIST].fillna(0).astype(int)
        y = df['prognosis']

        # Encode disease labels
        y_encoded = self.label_encoder.fit_transform(y)

        return X, y_encoded

    def train_and_evaluate(self, csv_path=None):
        """
        Train all models, evaluate, and identify the best performer.
        Returns: dict of accuracy results
        """
        logger.info("Starting model training pipeline...")

        # Load and preprocess data
        df = self.load_data(csv_path)
        X, y = self.preprocess_data(df)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        results = {}
        trained_models = {}

        for name, model in self.models.items():
            logger.info(f"Training {name}...")
            try:
                # Train
                model.fit(X_train, y_train)

                # Evaluate on test set
                y_pred = model.predict(X_test)
                test_accuracy = accuracy_score(y_test, y_pred)

                # Cross-validation
                cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
                cv_mean = cv_scores.mean()
                cv_std = cv_scores.std()

                results[name] = {
                    'test_accuracy': round(test_accuracy, 4),
                    'cv_mean': round(cv_mean, 4),
                    'cv_std': round(cv_std, 4),
                    'cv_scores': cv_scores.tolist(),
                }

                trained_models[name] = model
                logger.info(f"{name}: Test Acc={test_accuracy:.4f}, CV={cv_mean:.4f}±{cv_std:.4f}")

            except Exception as e:
                logger.error(f"Error training {name}: {e}")
                results[name] = {'error': str(e)}

        # Select best model based on cross-validation mean
        best_name = max(
            {k: v for k, v in results.items() if 'error' not in v},
            key=lambda k: results[k]['cv_mean']
        )

        self.best_model = trained_models[best_name]
        self.best_model_name = best_name
        self.accuracy_results = results

        logger.info(f"\nBest Model: {best_name} (CV Accuracy: {results[best_name]['cv_mean']:.4f})")

        # Save all models
        self.save_models(trained_models)

        return results

    def save_models(self, trained_models):
        """Save all trained models and supporting objects to disk."""
        try:
            # Save each model
            for name, model in trained_models.items():
                filename = name.lower().replace(' ', '_') + '.pkl'
                path = MODELS_DIR / filename
                with open(path, 'wb') as f:
                    pickle.dump(model, f)

            # Save label encoder
            with open(MODELS_DIR / 'label_encoder.pkl', 'wb') as f:
                pickle.dump(self.label_encoder, f)

            # Save accuracy results
            with open(MODELS_DIR / 'accuracy_results.pkl', 'wb') as f:
                pickle.dump(self.accuracy_results, f)

            # Save best model name
            with open(MODELS_DIR / 'best_model_name.txt', 'w') as f:
                f.write(self.best_model_name)

            # Save feature names
            with open(MODELS_DIR / 'feature_names.pkl', 'wb') as f:
                pickle.dump(self.feature_names, f)

            logger.info(f"All models saved to {MODELS_DIR}")

        except Exception as e:
            logger.error(f"Error saving models: {e}")
            raise

    def load_models(self):
        """Load trained models from disk."""
        try:
            # Load label encoder
            with open(MODELS_DIR / 'label_encoder.pkl', 'rb') as f:
                self.label_encoder = pickle.load(f)

            # Load best model name
            with open(MODELS_DIR / 'best_model_name.txt', 'r') as f:
                self.best_model_name = f.read().strip()

            # Load best model
            filename = self.best_model_name.lower().replace(' ', '_') + '.pkl'
            with open(MODELS_DIR / filename, 'rb') as f:
                self.best_model = pickle.load(f)

            # Load accuracy results
            with open(MODELS_DIR / 'accuracy_results.pkl', 'rb') as f:
                self.accuracy_results = pickle.load(f)

            logger.info(f"Loaded best model: {self.best_model_name}")
            return True

        except FileNotFoundError:
            logger.warning("Trained models not found. Please run train_models first.")
            return False

    def predict(self, symptoms_list):
        """
        Make a prediction given a list of symptom names.

        Args:
            symptoms_list (list): List of symptom name strings

        Returns:
            dict: Prediction results with disease, probability, and alternatives
        """
        if self.best_model is None:
            if not self.load_models():
                # Train new models if none exist
                self.train_and_evaluate()

        # Create feature vector
        feature_vector = np.zeros(len(SYMPTOM_LIST))
        for symptom in symptoms_list:
            symptom_clean = symptom.strip().lower().replace(' ', '_')
            if symptom_clean in SYMPTOM_LIST:
                idx = SYMPTOM_LIST.index(symptom_clean)
                feature_vector[idx] = 1

        feature_vector = feature_vector.reshape(1, -1)

        # Get prediction and probabilities
        predicted_encoded = self.best_model.predict(feature_vector)[0]
        predicted_disease = self.label_encoder.inverse_transform([predicted_encoded])[0]

        # Get probabilities for all diseases
        if hasattr(self.best_model, 'predict_proba'):
            probabilities = self.best_model.predict_proba(feature_vector)[0]
            disease_probabilities = {
                self.label_encoder.inverse_transform([i])[0]: float(prob)
                for i, prob in enumerate(probabilities)
            }
            confidence = probabilities[predicted_encoded]
        else:
            disease_probabilities = {predicted_disease: 1.0}
            confidence = 1.0

        # Get top 5 alternative predictions
        sorted_probs = sorted(disease_probabilities.items(), key=lambda x: x[1], reverse=True)
        top_predictions = [
            {'disease': d, 'probability': round(p * 100, 1)}
            for d, p in sorted_probs[:5]
        ]

        return {
            'predicted_disease': predicted_disease,
            'confidence': float(confidence),
            'confidence_percentage': f"{confidence * 100:.1f}%",
            'top_predictions': top_predictions,
            'model_used': self.best_model_name,
            'symptoms_matched': [s for s in symptoms_list if s.replace(' ', '_') in SYMPTOM_LIST],
        }

    def compare_all_models(self, symptoms_list):
        """
        Run prediction using all available models and compare results.

        Returns:
            dict: Results from each model
        """
        feature_vector = np.zeros(len(SYMPTOM_LIST))
        for symptom in symptoms_list:
            symptom_clean = symptom.strip().lower().replace(' ', '_')
            if symptom_clean in SYMPTOM_LIST:
                idx = SYMPTOM_LIST.index(symptom_clean)
                feature_vector[idx] = 1

        feature_vector = feature_vector.reshape(1, -1)

        comparison = {}
        model_files = {
            'Decision Tree': 'decision_tree.pkl',
            'Random Forest': 'random_forest.pkl',
            'Naive Bayes': 'naive_bayes.pkl',
            'SVM': 'svm.pkl',
        }

        for model_name, filename in model_files.items():
            model_path = MODELS_DIR / filename
            if model_path.exists():
                try:
                    with open(model_path, 'rb') as f:
                        model = pickle.load(f)

                    pred_encoded = model.predict(feature_vector)[0]
                    pred_disease = self.label_encoder.inverse_transform([pred_encoded])[0]

                    if hasattr(model, 'predict_proba'):
                        proba = model.predict_proba(feature_vector)[0][pred_encoded]
                    else:
                        proba = 1.0

                    comparison[model_name] = {
                        'predicted_disease': pred_disease,
                        'confidence': round(float(proba) * 100, 1),
                        'test_accuracy': self.accuracy_results.get(model_name, {}).get('test_accuracy', 'N/A'),
                        'cv_accuracy': self.accuracy_results.get(model_name, {}).get('cv_mean', 'N/A'),
                    }
                except Exception as e:
                    comparison[model_name] = {'error': str(e)}

        return comparison

    def get_accuracy_summary(self):
        """Return accuracy summary for all trained models."""
        if not self.accuracy_results:
            self.load_models()
        return self.accuracy_results


# ─── Global singleton instance ─────────────────────────────────────────────────
_engine_instance = None


def get_prediction_engine():
    """Get or create the global prediction engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = HealthcarePredictionEngine()
        _engine_instance.load_models()
    return _engine_instance


# ─── CLI interface for training ────────────────────────────────────────────────
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Healthcare ML Training')
    parser.add_argument('--train', action='store_true', help='Train all models')
    parser.add_argument('--dataset', type=str, help='Path to CSV dataset', default=None)
    parser.add_argument('--predict', type=str, help='Comma-separated symptoms for prediction')
    args = parser.parse_args()

    engine = HealthcarePredictionEngine()

    if args.train:
        print("\n🏥 Training Healthcare Prediction Models...")
        results = engine.train_and_evaluate(csv_path=args.dataset)
        print("\n📊 Model Accuracy Results:")
        print("=" * 60)
        for model_name, result in results.items():
            if 'error' not in result:
                print(f"{model_name:20s}: Test={result['test_accuracy']:.4f}, "
                      f"CV={result['cv_mean']:.4f}±{result['cv_std']:.4f}")
        print(f"\n✅ Best Model: {engine.best_model_name}")

    if args.predict:
        symptoms = [s.strip() for s in args.predict.split(',')]
        print(f"\n🔍 Predicting for symptoms: {symptoms}")
        result = engine.predict(symptoms)
        print(f"Predicted Disease: {result['predicted_disease']}")
        print(f"Confidence: {result['confidence_percentage']}")
        print(f"Model Used: {result['model_used']}")
