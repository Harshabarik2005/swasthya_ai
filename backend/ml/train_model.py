"""
ML Model Training Pipeline for Wellness Recommendations
Trains Random Forest classifiers for yoga, exercise, and ayurveda recommendations
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
import json

class WellnessMLTrainer:
    def __init__(self, dataset_path='datasets/wellness_ml_dataset.csv'):
        """Initialize the trainer"""
        self.dataset_path = dataset_path
        self.df = None
        self.encoders = {}
        self.models = {}
        self.feature_names = []
        
    def load_data(self):
        """Load and prepare the dataset"""
        print("Loading dataset...")
        self.df = pd.read_csv(self.dataset_path)
        print(f"✓ Loaded {len(self.df)} records")
        print(f"  Conditions: {self.df['condition'].nunique()}")
        print(f"  Features: {list(self.df.columns)}\n")
        
    def prepare_features(self):
        """Encode categorical features"""
        print("Encoding features...")
        
        # Features to encode
        categorical_features = ['condition', 'age_group', 'gender', 'severity', 
                               'bmi_category', 'activity_level']
        
        # Create encoders and transform
        X_encoded = self.df.copy()
        
        for feature in categorical_features:
            if feature in X_encoded.columns:
                encoder = LabelEncoder()
                X_encoded[feature + '_encoded'] = encoder.fit_transform(X_encoded[feature])
                self.encoders[feature] = encoder
                print(f"  {feature}: {len(encoder.classes_)} classes")
        
        # Select features for training
        self.feature_names = [
            'condition_encoded', 'age', 'age_group_encoded', 'gender_encoded',
            'severity_encoded', 'has_bp', 'has_diabetes', 'bmi_category_encoded',
            'activity_level_encoded', 'time_available'
        ]
        
        X = X_encoded[self.feature_names]
        
        # Target variables
        y_yoga = self.df['yoga_category']
        y_exercise = self.df['exercise_category']
        y_ayurveda = self.df['ayurveda_category']
        
        # Encode targets
        self.encoders['yoga_category'] = LabelEncoder()
        self.encoders['exercise_category'] = LabelEncoder()
        self.encoders['ayurveda_category'] = LabelEncoder()
        
        y_yoga_encoded = self.encoders['yoga_category'].fit_transform(y_yoga)
        y_exercise_encoded = self.encoders['exercise_category'].fit_transform(y_exercise)
        y_ayurveda_encoded = self.encoders['ayurveda_category'].fit_transform(y_ayurveda)
        
        print(f"\n✓ Feature matrix shape: {X.shape}")
        print(f"  Yoga categories: {len(self.encoders['yoga_category'].classes_)}")
        print(f"  Exercise categories: {len(self.encoders['exercise_category'].classes_)}")
        print(f"  Ayurveda categories: {len(self.encoders['ayurveda_category'].classes_)}\n")
        
        return X, y_yoga_encoded, y_exercise_encoded, y_ayurveda_encoded
    
    def train_models(self, X, y_yoga, y_exercise, y_ayurveda):
        """Train Random Forest models"""
        print("Training models...")
        
        # Split data (80/20)
        X_train, X_test, y_yoga_train, y_yoga_test = train_test_split(
            X, y_yoga, test_size=0.2, random_state=42, stratify=y_yoga
        )
        _, _, y_ex_train, y_ex_test = train_test_split(
            X, y_exercise, test_size=0.2, random_state=42, stratify=y_exercise
        )
        _, _, y_ay_train, y_ay_test = train_test_split(
            X, y_ayurveda, test_size=0.2, random_state=42, stratify=y_ayurveda
        )
        
        print(f"  Training set: {len(X_train)} samples")
        print(f"  Test set: {len(X_test)} samples\n")
        
        # Train Yoga model
        print("Training Yoga Pose Classifier...")
        yoga_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        yoga_model.fit(X_train, y_yoga_train)
        yoga_pred = yoga_model.predict(X_test)
        yoga_acc = accuracy_score(y_yoga_test, yoga_pred)
        print(f"  ✓ Yoga Accuracy: {yoga_acc:.2%}")
        self.models['yoga'] = yoga_model
        
        # Train Exercise model
        print("\nTraining Exercise Classifier...")
        exercise_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        exercise_model.fit(X_train, y_ex_train)
        ex_pred = exercise_model.predict(X_test)
        ex_acc = accuracy_score(y_ex_test, ex_pred)
        print(f"  ✓ Exercise Accuracy: {ex_acc:.2%}")
        self.models['exercise'] = exercise_model
        
        # Train Ayurveda model
        print("\nTraining Ayurveda Classifier...")
        ayurveda_model = RandomForestClassifier(
            n_estimators=100,
max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        ayurveda_model.fit(X_train, y_ay_train)
        ay_pred = ayurveda_model.predict(X_test)
        ay_acc = accuracy_score(y_ay_test, ay_pred)
        print(f"  ✓ Ayurveda Accuracy: {ay_acc:.2%}\n")
        self.models['ayurveda'] = ayurveda_model
        
        # Feature importance
        print("Top 5 Important Features:")
        feature_imp = pd.DataFrame({
            'feature': self.feature_names,
            'importance': yoga_model.feature_importances_
        }).sort_values('importance', ascending=False)
        print(feature_imp.head())
        
        return {
            'yoga': yoga_acc,
            'exercise': ex_acc,
            'ayurveda': ay_acc
        }
    
    def save_models(self):
        """Save trained models and encoders"""
        print("\nSaving models...")
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        # Save models
        joblib.dump(self.models['yoga'], 'models/yoga_model.pkl')
        joblib.dump(self.models['exercise'], 'models/exercise_model.pkl')
        joblib.dump(self.models['ayurveda'], 'models/ayurveda_model.pkl')
        
        # Save encoders
        joblib.dump(self.encoders, 'models/encoders.pkl')
        
        # Save feature names
        with open('models/feature_names.json', 'w') as f:
            json.dump(self.feature_names, f)
        
        print("✓ Models saved to models/")
        print("  - yoga_model.pkl")
        print("  - exercise_model.pkl")
        print("  - ayurveda_model.pkl")
        print("  - encoders.pkl")
        print("  - feature_names.json")
    
    def train(self):
        """Run complete training pipeline"""
        self.load_data()
        X, y_yoga, y_exercise, y_ayurveda = self.prepare_features()
        accuracies = self.train_models(X, y_yoga, y_exercise, y_ayurveda)
        self.save_models()
        
        print(f"\n{'='*50}")
        print("TRAINING COMPLETE!")
        print(f"{'='*50}")
        print(f"Yoga Model Accuracy:     {accuracies['yoga']:.2%}")
        print(f"Exercise Model Accuracy: {accuracies['exercise']:.2%}")
        print(f"Ayurveda Model Accuracy: {accuracies['ayurveda']:.2%}")
        print(f"{'='*50}\n")

if __name__ == '__main__':
    trainer = WellnessMLTrainer()
    trainer.train()
