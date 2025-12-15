"""
Enhanced Wellness Dataset Generator
Creates comprehensive training data for ML recommendation system
"""
import pandas as pd
import random
from itertools import product

# Define all possible values for each feature
CONDITIONS = ['stress', 'migraine', 'pcod', 'back pain', 'knee pain', 'joint pain', 'regular exercise']
AGE_RANGES = [(6, 17, 'child'), (18, 35, 'young_adult'), (36, 50, 'adult'), (51, 54, 'senior')]
GENDERS = ['male', 'female', 'other']
SEVERITIES = ['mild', 'moderate', 'severe']
BMI_CATEGORIES = ['underweight', 'normal', 'overweight', 'obese']
ACTIVITY_LEVELS = ['sedentary', 'moderate', 'active']

# Yoga poses by category and suitability
YOGA_POSES = {
    'relaxation': {
        'poses': ['shavasana.jpg', 'sukhasana.jpg', 'balasana.jpg', 'viparita_karani.jpg'],
        'suitable_for': ['stress', 'migraine', 'regular exercise']
    },
    'flexibility': {
        'poses': ['paschimottanasana.jpg', 'uttanasana.jpg', 'trikonasana.jpg', 'ardha_matsyendrasana.jpg'],
        'suitable_for': ['back pain', 'regular exercise']
    },
    'strength': {
        'poses': ['virabhadrasana.jpg', 'chaturanga.jpg', 'navasana.jpg', 'plank.jpg'],
        'suitable_for': ['regular exercise', 'joint pain']
    },
    'breathing': {
        'poses': ['pranayama.jpg', 'anulom_vilom.jpg', 'kapalbhati.jpg', 'bhramari.jpg'],
        'suitable_for': ['stress', 'migraine']
    },
    'hormonal': {
        'poses': ['baddha_konasana.jpg', 'setu_bandhasana.jpg', 'malasana.jpg', 'supta_baddha_konasana.jpg'],
        'suitable_for': ['pcod']
    },
    'joint_health': {
        'poses': ['pawanmuktasana.jpg', 'gomukhasana.jpg', 'marjaryasana.jpg', 'cat_cow.jpg'],
        'suitable_for': ['knee pain', 'joint pain', 'back pain']
    }
}

# Exercises by category
EXERCISES = {
    'cardio': {
        'exercises': ['brisk_walk.jpg', 'jogging.jpg', 'cycling.jpg', 'swimming.jpg'],
        'suitable_for': ['stress', 'regular exercise', 'pcod']
    },
    'strength': {
        'exercises': ['bodyweight_squats.jpg', 'push_ups.jpg', 'resistance_band.jpg', 'wall_push.jpg'],
        'suitable_for': ['regular exercise', 'back pain']
    },
    'flexibility': {
        'exercises': ['stretching.jpg', 'yoga_flow.jpg', 'pilates.jpg', 'tai_chi.jpg'],
        'suitable_for': ['joint pain', 'back pain', 'knee pain']
    },
    'low_impact': {
        'exercises': ['walking.jpg', 'water_aerobics.jpg', 'gentle_stretching.jpg', 'chair_exercises.jpg'],
        'suitable_for': ['migraine', 'knee pain', 'joint pain']
    }
}

# Ayurveda remedies by category
AYURVEDA = {
    'herbal_tea': {
        'remedies': ['ashwagandha_tea.jpg', 'ginger_tea.jpg', 'lavender_tea.jpg', 'chamomile_tea.jpg', 'green_tea.jpg', 'turmeric_milk.jpg'],
        'suitable_for': ['stress', 'migraine', 'pcod']
    },
    'oil_massage': {
        'remedies': ['warm_oil_massage.jpg', 'head_massage_oil.jpg', 'sesame_oil.jpg', 'coconut_oil.jpg'],
        'suitable_for': ['migraine', 'joint pain', 'knee pain', 'back pain']
    },
    'dietary': {
        'remedies': ['cinnamon_tea.jpg', 'fenugreek_seeds.jpg', 'triphala.jpg', 'amla_juice.jpg'],
        'suitable_for': ['pcod', 'stress']
    },
    'powder': {
        'remedies': ['ashwagandha_powder.jpg', 'turmeric_powder.jpg', 'brahmi_powder.jpg'],
        'suitable_for': ['stress', 'joint pain']
    }
}

# Safety rules - poses to avoid for certain conditions
UNSAFE_POSES = {
    'has_bp': ['shirshasana.jpg', 'sarvangasana.jpg', 'halasana.jpg', 'kapalbhati.jpg'],
    'has_diabetes': ['shirshasana.jpg', 'sarvangasana.jpg'],
    'knee_pain': ['padmasana.jpg', 'vajrasana.jpg'],
    'recent_pregnancy': ['chakrasana.jpg', 'kapalbhati.jpg']
}

def get_age_group(age):
    """Categorize age into groups"""
    for min_age, max_age, group in AGE_RANGES:
        if min_age <= age <= max_age:
            return group
    return 'adult'

def select_yoga_pose(condition, has_bp, has_diabetes, severity):
    """Select appropriate yoga pose based on condition and constraints"""
    # Find suitable categories for the condition
    suitable_categories = []
    for category, info in YOGA_POSES.items():
        if condition in info['suitable_for']:
            suitable_categories.append(category)
    
    if not suitable_categories:
        suitable_categories = ['relaxation']  # Default
    
    # Select random category
    category = random.choice(suitable_categories)
    poses = YOGA_POSES[category]['poses'].copy()
    
    # Filter out unsafe poses
    if has_bp:
        poses = [p for p in poses if p not in UNSAFE_POSES['has_bp']]
    if has_diabetes:
        poses = [p for p in poses if p not in UNSAFE_POSES['has_diabetes']]
    
    if not poses:
        poses = ['shavasana.jpg']  # Safe default
    
    return random.choice(poses), category

def select_exercise(condition, age_group, bmi_category):
    """Select appropriate exercise"""
    suitable_categories = []
    for category, info in EXERCISES.items():
        if condition in info['suitable_for']:
            suitable_categories.append(category)
    
    if not suitable_categories:
        suitable_categories = ['low_impact']
    
    # Seniors and overweight prefer low impact
    if age_group == 'senior' or bmi_category == 'obese':
        if 'low_impact' in EXERCISES:
            suitable_categories = ['low_impact']
    
    category = random.choice(suitable_categories)
    exercise = random.choice(EXERCISES[category]['exercises'])
    return exercise, category

def select_ayurveda(condition, severity):
    """Select appropriate ayurveda remedy"""
    suitable_categories = []
    for category, info in AYURVEDA.items():
        if condition in info['suitable_for']:
            suitable_categories.append(category)
    
    if not suitable_categories:
        suitable_categories = ['herbal_tea']
    
    category = random.choice(suitable_categories)
    remedy = random.choice(AYURVEDA[category]['remedies'])
    return remedy, category

def generate_dataset(num_records=800):
    """Generate comprehensive training dataset"""
    data = []
    record_id = 1
    
    # Generate records for each condition
    for condition in CONDITIONS:
        # Number of records per condition (varied based on importance)
        records_per_condition = num_records // len(CONDITIONS)
        
        for _ in range(records_per_condition):
            # Random age
            age_range = random.choice(AGE_RANGES)
            age = random.randint(age_range[0], age_range[1])
            age_group = age_range[2]
            
            # Random gender (more female for PCOD)
            if condition == 'pcod':
                gender = 'female'
            else:
                gender = random.choice(GENDERS)
            
            # Random severity (skip for regular exercise)
            if condition == 'regular exercise':
                severity = 'mild'
            else:
                severity = random.choice(SEVERITIES)
            
            # Random health conditions
            has_bp = random.choice([0, 1]) if random.random() < 0.15 else 0
            has_diabetes = random.choice([0, 1]) if random.random() < 0.15 else 0
            
            # Random BMI and activity level
            bmi_category = random.choice(BMI_CATEGORIES)
            activity_level = random.choice(ACTIVITY_LEVELS)
            
            # Time available (10-60 minutes)
            time_available = random.choice([10, 15, 20, 30, 45, 60])
            
            # Select recommendations
            yoga_pose, yoga_category = select_yoga_pose(condition, has_bp, has_diabetes, severity)
            exercise, exercise_category = select_exercise(condition, age_group, bmi_category)
            ayurveda, ayurveda_category = select_ayurveda(condition, severity)
            
            # Create record
            record = {
                'id': record_id,
                'condition': condition,
                'age': age,
                'age_group': age_group,
                'gender': gender,
                'severity': severity,
                'has_bp': has_bp,
                'has_diabetes': has_diabetes,
                'bmi_category': bmi_category,
                'activity_level': activity_level,
                'time_available': time_available,
                'yoga_pose': yoga_pose,
                'exercise': exercise,
                'ayurveda_tip': ayurveda,
                'yoga_category': yoga_category,
                'exercise_category': exercise_category,
                'ayurveda_category': ayurveda_category
            }
            
            data.append(record)
            record_id += 1
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Shuffle the dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return df

if __name__ == '__main__':
    print("Generating enhanced wellness dataset...")
    df = generate_dataset(800)
    
    # Save to CSV
    output_path = 'datasets/wellness_ml_dataset.csv'
    df.to_csv(output_path, index=False)
    
    print(f"✓ Dataset created: {output_path}")
    print(f"  Total records: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    print(f"\nRecords per condition:")
    print(df['condition'].value_counts())
    print(f"\nAge group distribution:")
    print(df['age_group'].value_counts())
    print(f"\nGender distribution:")
    print(df['gender'].value_counts())
    print(f"\nFirst few records:")
    print(df.head())
