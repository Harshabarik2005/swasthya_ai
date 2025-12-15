import pandas as pd

def load_dataset(path="ai_wellness_data.xlsx"):
    # Determine file type and load accordingly
    if path.endswith('.csv'):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)
    
    df.columns = [c.strip().lower() for c in df.columns]

    required = {"condition", "age", "severity", "yoga_pose", "exercise", "ayurveda_tip"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing columns: {required - set(df.columns)}")

    df["condition"] = df["condition"].astype(str).str.strip().str.lower()
    df["severity"] = df["severity"].astype(str).str.strip().str.lower()
    df["activity_level"] = df["activity_level"].astype(str).str.strip().str.lower()
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    return df

def match_recommendation(df, condition, age, severity, time_available=None, gender=None, 
                         activity_level=None, bmi_category=None, has_bp=False, has_diabetes=False):
    """
    Find the best matching recommendation based on multiple criteria.
    Uses a scoring system to rank matches when multiple options exist.
    """
    condition = str(condition).strip().lower()
    severity = str(severity).strip().lower()
    
    # Start with condition and severity match
    matches = df[(df["condition"] == condition) & (df["severity"] == severity)]
    
    print(f"DEBUG: Looking for condition='{condition}', severity='{severity}'")
    print(f"DEBUG: Found {len(matches)} matches with exact severity")
    
    # If no exact severity match, try condition only
    if matches.empty:
        matches = df[df["condition"] == condition]
        print(f"DEBUG: Fallback - Found {len(matches)} matches with condition only")
    
    if matches.empty:
        print("DEBUG: No matches found at all")
        return None
    
    # If only one match, return it
    if len(matches) == 1:
        row = matches.iloc[0]
        print(f"DEBUG: Only one match found - returning it directly")
        return {
            "condition": row["condition"],
            "yogapose": row["yoga_pose"],
            "exercise": row["exercise"],
            "ayurveda_tip": row["ayurveda_tip"]
        }
    
    # Multiple matches found - score them to find the best one
    print(f"DEBUG: Multiple matches ({len(matches)}) - scoring them...")
    matches = matches.copy()
    matches['score'] = 0
    
    # Score by time_available (closer is better)
    if time_available is not None:
        time_available = int(time_available)
        matches['time_diff'] = abs(matches['time_available'] - time_available)
        # Give higher score to closer time matches (inverse scoring)
        max_time_diff = matches['time_diff'].max()
        if max_time_diff > 0:
            matches['score'] += (1 - (matches['time_diff'] / max_time_diff)) * 3  # Weight: 3 points
    
    # Score by age proximity
    if age is not None:
        age = int(age)
        matches['age_diff'] = abs(matches['age'] - age)
        max_age_diff = matches['age_diff'].max()
        if max_age_diff > 0:
            matches['score'] += (1 - (matches['age_diff'] / max_age_diff)) * 2  # Weight: 2 points
    
    # Exact match bonuses
    if gender is not None:
        gender_lower = str(gender).strip().lower()
        matches.loc[matches['gender'] == gender_lower, 'score'] += 1.5  # Weight: 1.5 points
    
    if activity_level is not None:
        activity_lower = str(activity_level).strip().lower()
        matches.loc[matches['activity_level'] == activity_lower, 'score'] += 1.5  # Weight: 1.5 points
    
    if bmi_category is not None:
        bmi_lower = str(bmi_category).strip().lower()
        matches.loc[matches['bmi_category'] == bmi_lower, 'score'] += 1  # Weight: 1 point
    
    # Health condition matches
    if has_bp:
        matches.loc[matches['has_bp'] == 1, 'score'] += 1  # Weight: 1 point
    
    if has_diabetes:
        matches.loc[matches['has_diabetes'] == 1, 'score'] += 1  # Weight: 1 point
    
    # Get the best match (highest score)
    best_match = matches.loc[matches['score'].idxmax()]
    
    print(f"DEBUG: Parameters passed - time_available={time_available}, gender={gender}, activity_level={activity_level}, bmi_category={bmi_category}")
    print(f"DEBUG: Best match score: {best_match['score']}")
    print(f"DEBUG: Selected exercise: {best_match['exercise']}, yoga: {best_match['yoga_pose']}")
    
    return {
        "condition": best_match["condition"],
        "yogapose": best_match["yoga_pose"],
        "exercise": best_match["exercise"],
        "ayurveda_tip": best_match["ayurveda_tip"]
    }
