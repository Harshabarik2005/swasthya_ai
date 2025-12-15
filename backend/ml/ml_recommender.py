"""
ML-based Wellness Recommender
Provides intelligent recommendations using trained Random Forest models
"""
import pandas as pd
import joblib
import os
import json
import random

class MLRecommender:
    def __init__(self, models_dir='models'):
        """Initialize ML recommender with trained models"""
        self.models_dir = models_dir
        self.models = {}
        self.encoders = {}
        self.feature_names = []
        self.recommendation_mappings = {}
        self.load_models()
        self.load_mappings()
        
    def load_models(self):
        """Load trained models and encoders"""
        try:
            self.models['yoga'] = joblib.load(os.path.join(self.models_dir, 'yoga_model.pkl'))
            self.models['exercise'] = joblib.load(os.path.join(self.models_dir, 'exercise_model.pkl'))
            self.models['ayurveda'] = joblib.load(os.path.join(self.models_dir, 'ayurveda_model.pkl'))
            self.encoders = joblib.load(os.path.join(self.models_dir, 'encoders.pkl'))
            
            with open(os.path.join(self.models_dir, 'feature_names.json'), 'r') as f:
                self.feature_names = json.load(f)
            
            print("✓ ML models loaded successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to load ML models: {e}")
            return False
    
    def load_mappings(self):
        """Load category-to-recommendation mappings"""
        self.recommendation_mappings = {
            'yoga': {
                'relaxation': ['shavasana.jpg', 'sukhasana.jpg', 'balasana.jpg', 'viparita_karani.jpg'],
                'flexibility': ['uttanasana.jpg', 'trikonasana.jpg', 'side_bends.jpg', 'cat_cow_pose.jpg'],
                'strength': ['virabhadrasana.jpg', 'bhujangasana.jpg', 'core_strength.jpg', 'setu_bandhasana.jpg'],
                'breathing': ['deep_breathing.jpg', 'anulom_vilom.jpg', 'breathing_drill.jpg', 'deep_breathing.jpg'],
                'hormonal': ['baddha_konasana.jpg', 'setu_bandhasana.jpg', 'malasana.jpg', 'supta_baddha_konasana.jpg'],
                'joint_health': ['balasana.jpg', 'shoulder_rolls.jpg', 'cat_cow_pose.jpg', 'mobility_exercise.jpg']
            },
            'exercise': {
                'cardio': ['brisk_walking.jpg', 'light_jog.jpg', 'cycling.jpg', 'jumping_jacks.jpg'],
                'strength': ['step_ups.jpg', 'core_strength.jpg', 'stretching.jpg', 'hand_rotation.jpg'],
                'flexibility': ['stretching.jpg', 'sun_salutation.jpg', 'core_strength.jpg', 'balance_training.jpg'],
                'low_impact': ['slow_walking.jpg', 'mobility_exercise.jpg', 'stretching.jpg', 'sukhasana.jpg']
            },
            'ayurveda': {
                'herbal_tea': ['herbal_tea.jpg', 'ginger_tea.jpg', 'lavender_tea.jpg', 'green_tea.jpg', 'turmeric_milk.jpg', 'hibiscus_tea.jpg'],
                'oil_massage': ['warm_oil_massage.jpg', 'head_massage_oil.jpg', 'warm_oil_massage.jpg', 'head_massage_oil.jpg'],
                'dietary': ['cinnamon_tea.jpg', 'diet_control.jpg', 'herbal_tea.jpg', 'lemon_water.jpg'],
                'powder': ['ashwagandha_powder.jpg', 'turmeric_milk.jpg', 'ashwagandha_powder.jpg']
            }
        }
    
    def get_age_group(self, age):
        """Convert age to age group"""
        if age <= 17:
            return 'child'
        elif age <= 35:
            return 'young_adult'
        elif age <= 50:
            return 'adult'
        else:
            return 'senior'
    
    def prepare_features(self, user_data):
        """Prepare features for prediction with engineered features"""
        try:
            # Extract user data
            condition = str(user_data.get('condition', 'stress')).strip().lower()
            age = int(user_data.get('age', 30))
            gender = str(user_data.get('gender', 'other')).strip().lower()
            severity = str(user_data.get('severity', 'mild')).strip().lower()
            has_bp = int(user_data.get('has_bp', 0))
            has_diabetes = int(user_data.get('has_diabetes', 0))
            bmi_category = str(user_data.get('bmi_category', 'normal')).strip().lower()
            activity_level = str(user_data.get('activity_level', 'moderate')).strip().lower()
            time_available = int(user_data.get('time_available', 30))
            
            # Get age group
            age_group = self.get_age_group(age)
            
            # Engineer additional features
            is_senior = 1 if age >= 51 else 0
            is_child = 1 if age <= 17 else 0
            health_risk = has_bp + has_diabetes
            
            severity_map = {'mild': 1, 'moderate': 2, 'severe': 3}
            severity_numeric = severity_map.get(severity, 1)
            
            bmi_risk_map = {'underweight': 2, 'normal': 0, 'overweight': 1, 'obese': 3}
            bmi_risk = bmi_risk_map.get(bmi_category, 0)
            
            activity_map = {'sedentary': 0, 'moderate': 1, 'active': 2}
            activity_score = activity_map.get(activity_level, 1)
            
            # Create feature dictionary
            features = {
                'condition': condition,
                'age': age,
                'age_group': age_group,
                'gender': gender,
                'severity': severity,
                'bmi_category': bmi_category,
                'activity_level': activity_level
            }
            
            # Encode categorical features
            encoded_features = {}
            for feat, value in features.items():
                if feat + '_encoded' in self.feature_names:
                    encoder = self.encoders.get(feat)
                    if encoder:
                        try:
                            encoded_features[feat + '_encoded'] = encoder.transform([value])[0]
                        except:
                            # Use default if value not in training data
                            encoded_features[feat + '_encoded'] = 0
            
            # Add numeric and engineered features
            encoded_features['age'] = age
            encoded_features['has_bp'] = has_bp
            encoded_features['has_diabetes'] = has_diabetes
            encoded_features['time_available'] = time_available
            encoded_features['is_senior'] = is_senior
            encoded_features['is_child'] = is_child
            encoded_features['health_risk'] = health_risk
            encoded_features['severity_numeric'] = severity_numeric
            encoded_features['bmi_risk'] = bmi_risk
            encoded_features['activity_score'] = activity_score
            
            # Create feature vector in correct order
            X = [encoded_features.get(feat, 0) for feat in self.feature_names]
            
            return [X], True
            
        except Exception as e:
            print(f"Error preparing features: {e}")
            return None, False
    
    def predict(self, user_data):
        """Make ML-based recommendations"""
        try:
            # Prepare features
            X, success = self.prepare_features(user_data)
            if not success or X is None:
                return None, 0.0
            
            # Make predictions
            yoga_category_encoded = self.models['yoga'].predict(X)[0]
            exercise_category_encoded = self.models['exercise'].predict(X)[0]
            ayurveda_category_encoded = self.models['ayurveda'].predict(X)[0]
            
            # Get prediction probabilities (confidence)
            yoga_proba = max(self.models['yoga'].predict_proba(X)[0])
            exercise_proba = max(self.models['exercise'].predict_proba(X)[0])
            ayurveda_proba = max(self.models['ayurveda'].predict_proba(X)[0])
            
            # Average confidence
            avg_confidence = (yoga_proba + exercise_proba + ayurveda_proba) / 3
            
            # Decode categories
            yoga_category = self.encoders['yoga_category'].inverse_transform([yoga_category_encoded])[0]
            exercise_category = self.encoders['exercise_category'].inverse_transform([exercise_category_encoded])[0]
            ayurveda_category = self.encoders['ayurveda_category'].inverse_transform([ayurveda_category_encoded])[0]
            
            # Map to specific recommendations
            yoga_options = self.recommendation_mappings['yoga'].get(yoga_category, ['shavasana.jpg'])
            exercise_options = self.recommendation_mappings['exercise'].get(exercise_category, ['walking.jpg'])
            ayurveda_options = self.recommendation_mappings['ayurveda'].get(ayurveda_category, ['green_tea.jpg'])
            
            # Apply safety rules
            has_bp = user_data.get('has_bp', 0)
            has_diabetes = user_data.get('has_diabetes', 0)
            
            unsafe_poses = []
            if has_bp:
                unsafe_poses.extend(['shirshasana.jpg', 'sarvangasana.jpg', 'halasana.jpg', 'breathing_drill.jpg'])
            if has_diabetes:
                unsafe_poses.extend(['shirshasana.jpg', 'sarvangasana.jpg'])
            
            # Filter unsafe poses
            safe_yoga_options = [pose for pose in yoga_options if pose not in unsafe_poses]
            if not safe_yoga_options:
                safe_yoga_options = ['shavasana.jpg']  # Safe default
            
            # Select recommendations
            yoga_pose = random.choice(safe_yoga_options)
            exercise = random.choice(exercise_options)
            ayurveda_tip = random.choice(ayurveda_options)
            
            recommendation = {
                'yogapose': yoga_pose,
                'exercise': exercise,
                'ayurveda_tip': ayurveda_tip,
                'yoga_category': yoga_category,
                'exercise_category': exercise_category,
                'ayurveda_category': ayurveda_category,
                'ml_confidence': round(avg_confidence * 100, 2),
                'method': 'ml'
            }
            
            return recommendation, avg_confidence
            
        except Exception as e:
            print(f"ML prediction error: {e}")
            import traceback
            traceback.print_exc()
            return None, 0.0
    
    def get_recommendation(self, user_data, confidence_threshold=0.3):
        """Get recommendation with confidence check"""
        rec, confidence = self.predict(user_data)
        
        if rec and confidence >= confidence_threshold:
            print(f"✓ ML recommendation (confidence: {confidence:.2%})")
            return rec
        else:
            print(f"✗ ML confidence low ({confidence:.2%}), use fallback")
            return None

# Global ML recommender instance
ml_recommender = None

def get_ml_recommender():
    """Get or create ML recommender instance"""
    global ml_recommender
    if ml_recommender is None:
        try:
            ml_recommender = MLRecommender()
        except Exception as e:
            print(f"Failed to initialize ML recommender: {e}")
            ml_recommender = None
    return ml_recommender
