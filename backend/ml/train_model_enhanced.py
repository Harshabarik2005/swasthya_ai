"""
Enhanced ML Model Training Pipeline - Improved Accuracy
Uses hyperparameter tuning, more data, and better algorithms
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, f1_score
import joblib
import os
import json

class EnhancedWellnessMLTrainer:
    def __init__(self, dataset_path='datasets/wellness_ml_dataset.csv'):
        """Initialize the enhanced trainer"""
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
        
    def engineer_features(self):
        """Advanced feature engineering"""
        print("Engineering features...")
        
        # Age-based features
        self.df['is_senior'] = (self.df['age'] >= 51).astype(int)
        self.df['is_child'] = (self.df['age'] <= 17).astype(int)
        
        # Health risk score
        self.df['health_risk'] = self.df['has_bp'] + self.df['has_diabetes']
        
        # Severity encoding (ordinal)
        severity_map = {'mild': 1, 'moderate': 2, 'severe': 3}
        self.df['severity_numeric'] = self.df['severity'].map(severity_map)
        
        # BMI risk (ordinal)
        bmi_risk_map = {'underweight': 2, 'normal': 0, 'overweight': 1, 'obese': 3}
        self.df['bmi_risk'] = self.df['bmi_category'].map(bmi_risk_map)
        
        # Activity score
        activity_map = {'sedentary': 0, 'moderate': 1, 'active': 2}
        self.df['activity_score'] = self.df['activity_level'].map(activity_map)
        
        print("✓ Engineered additional features")
        
    def prepare_features(self):
        """Encode categorical features with engineered features"""
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
        
        # Select features for training (including engineered ones)
        self.feature_names = [
            'condition_encoded', 'age', 'age_group_encoded', 'gender_encoded',
            'severity_encoded', 'has_bp', 'has_diabetes', 'bmi_category_encoded',
            'activity_level_encoded', 'time_available',
            # Engineered features
            'is_senior', 'is_child', 'health_risk', 'severity_numeric',
            'bmi_risk', 'activity_score'
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
        
        print(f"✓ Feature matrix shape: {X.shape}")
        print(f"  Total features: {len(self.feature_names)}")
        print(f"  Yoga categories: {len(self.encoders['yoga_category'].classes_)}")
        print(f"  Exercise categories: {len(self.encoders['exercise_category'].classes_)}")
        print(f"  Ayurveda categories: {len(self.encoders['ayurveda_category'].classes_)}\n")
        
        return X, y_yoga_encoded, y_exercise_encoded, y_ayurveda_encoded
    
    def train_with_tuning(self, X, y, model_name):
        """Train model with hyperparameter tuning"""
        print(f"Training {model_name} with hyperparameter tuning...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Try Gradient Boosting (often better than Random Forest)
        param_grid = {
            'n_estimators': [100],
            'max_depth': [7],
            'learning_rate': [0.1],
            'min_samples_split': [5],
            'subsample': [0.8]
        }
        
        base_model = GradientBoostingClassifier(random_state=42)
        
        # Grid search
        grid_search = GridSearchCV(
            base_model, 
            param_grid, 
            cv=3,  # 3-fold cross-validation
            scoring='accuracy',
            n_jobs=-1,  # Use all CPU cores
            verbose=1
        )
        
        print(f"  Running grid search (this may take a minute)...")
        grid_search.fit(X_train, y_train)
        
        # Best model
        best_model = grid_search.best_estimator_
        
        # Evaluate
        y_pred = best_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        print(f"  ✓ Best params: {grid_search.best_params_}")
        print(f"  ✓ Accuracy: {accuracy:.2%}")
        print(f"  ✓ F1-Score: {f1:.2%}\n")
        
        return best_model, accuracy
    
    def train_models(self, X, y_yoga, y_exercise, y_ayurveda):
        """Train all models with tuning"""
        print("="*60)
        print("TRAINING MODELS WITH HYPERPARAMETER TUNING")
        print("="*60 + "\n")
        
        accuracies = {}
        
        # Train Yoga model
        yoga_model, yoga_acc = self.train_with_tuning(X, y_yoga, "Yoga Classifier")
        self.models['yoga'] = yoga_model
        accuracies['yoga'] = yoga_acc
        
        # Train Exercise model
        exercise_model, ex_acc = self.train_with_tuning(X, y_exercise, "Exercise Classifier")
        self.models['exercise'] = exercise_model
        accuracies['exercise'] = ex_acc
        
        # Train Ayurveda model
        ayurveda_model, ay_acc = self.train_with_tuning(X, y_ayurveda, "Ayurveda Classifier")
        self.models['ayurveda'] = ayurveda_model
        accuracies['ayurveda'] = ay_acc
        
        # Feature importance
        print("\nTop 10 Important Features:")
        feature_imp = pd.DataFrame({
            'feature': self.feature_names,
            'importance': yoga_model.feature_importances_
        }).sort_values('importance', ascending=False)
        print(feature_imp.head(10))
        
        return accuracies
    
    def save_models(self):
        """Save trained models and encoders"""
        print("\nSaving models...")
        
        os.makedirs('models', exist_ok=True)
        
        joblib.dump(self.models['yoga'], 'models/yoga_model.pkl')
        joblib.dump(self.models['exercise'], 'models/exercise_model.pkl')
        joblib.dump(self.models['ayurveda'], 'models/ayurveda_model.pkl')
        joblib.dump(self.encoders, 'models/encoders.pkl')
        
        with open('models/feature_names.json', 'w') as f:
            json.dump(self.feature_names, f)
        
        print("✓ Models saved to models/")
    
    def train(self):
        """Run complete enhanced training pipeline"""
        self.load_data()
        self.engineer_features()
        X, y_yoga, y_exercise, y_ayurveda = self.prepare_features()
        accuracies = self.train_models(X, y_yoga, y_exercise, y_ayurveda)
        self.save_models()
        
        print(f"\n{'='*60}")
        print("ENHANCED TRAINING COMPLETE!")
        print(f"{'='*60}")
        print(f"Yoga Model Accuracy:     {accuracies['yoga']:.2%}")
        print(f"Exercise Model Accuracy: {accuracies['exercise']:.2%}")
        print(f"Ayurveda Model Accuracy: {accuracies['ayurveda']:.2%}")
        avg_acc = (accuracies['yoga'] + accuracies['exercise'] + accuracies['ayurveda']) / 3
        print(f"Average Accuracy:        {avg_acc:.2%}")
        print(f"{'='*60}\n")

if __name__ == '__main__':
    trainer = EnhancedWellnessMLTrainer()
    trainer.train()
