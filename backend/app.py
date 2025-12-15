from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from pymongo import MongoClient
from recommender import load_dataset, match_recommendation
from ml.ml_recommender import get_ml_recommender
import os
import google.generativeai as genai

# ----------------------------------------------
#  INITIAL SETUP
# ----------------------------------------------
app = Flask(__name__)
CORS(app)

# ----------------------------------------------
#  DATABASE SETUP (MongoDB Atlas)
# ----------------------------------------------
# TODO: Replace YOUR_PASSWORD_HERE with your actual MongoDB Atlas password
MONGODB_URI = "mongodb+srv://harshabarik2005_db_user:harsha@cluster69.s2dwmsy.mongodb.net/?appName=Cluster69"
try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.server_info()
    print("✓ MongoDB connected successfully")
    db = client["wellness_ai"]
    users_col = db["users"]
    recs_col = db["recommendations"]
except Exception as e:
    print(f"✗ MongoDB connection failed: {e}")
    print("⚠ App will continue but database operations will fail")
    client = None
    db = None
    users_col = None
    recs_col = None

# ----------------------------------------------
#  DATASET SETUP
# ----------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "datasets", "ai_wellness_data_v2.csv")
dataset = load_dataset(DATA_PATH)

# ----------------------------------------------
#  GEMINI API SETUP
# ----------------------------------------------
GEMINI_API_KEY = "AIzaSyAfhuvpUuuT2UZao1LutPaLr6i2gtYPfkk"
genai.configure(api_key=GEMINI_API_KEY)

def get_chatbot_model():
    """Initialize and return Gemini model"""
    try:
        # Try gemini-2.5-flash (user requested)
        return genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        print(f"Failed to load gemini-2.5-flash: {e}")
        try:
            # Fallback to gemini-pro
            return genai.GenerativeModel('gemini-pro')
        except Exception as e2:
            print(f"Failed to load gemini-pro: {e2}")
            return None

# ----------------------------------------------
#  OTP & EMAIL SETUP
# ----------------------------------------------
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

otps_col = db["otps"]

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_email_otp(to_email, otp):
    # TODO: Configure your SMTP settings here
    # For now, we will PRINT the OTP to the console for testing
    print(f"\n{'='*30}")
    print(f"📧 EMAIL SIMULATION")
    print(f"To: {to_email}")
    print(f"Subject: Your Verification Code")
    print(f"Body: Your OTP is {otp}")
    print(f"{'='*30}\n")
    
    # UNCOMMENT AND CONFIGURE THE FOLLOWING TO SEND REAL EMAILS
    """
    sender_email = "your_email@gmail.com"
    sender_password = "your_app_password"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = "Swasthya AI - Email Verification"
        body = f"Hello,\n\nYour verification code for Swasthya AI is: {otp}\n\nThis code expires in 10 minutes."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False
    """
    return True

@app.route("/api/send-otp", methods=["POST"])
def send_otp():
    data = request.json
    email = data.get("email")
    
    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Validate email format (Must be @gmail.com as per requirements)
    if not email.endswith("@gmail.com"):
        return jsonify({"error": "Only @gmail.com email addresses are allowed"}), 400
        
    # Check if email is already registered
    if users_col.find_one({"email": email}):
        return jsonify({"error": "Email already registered. Please login."}), 400
        
    otp = generate_otp()
    
    # Store OTP with timestamp
    otps_col.update_one(
        {"email": email},
        {"$set": {
            "otp": otp, 
            "created_at": datetime.now(),
            "verified": False
        }},
        upsert=True
    )
    
    # Send email (or print to console)
    if send_email_otp(email, otp):
        return jsonify({"success": True, "message": "OTP sent successfully"})
    else:
        return jsonify({"error": "Failed to send OTP"}), 500

@app.route("/api/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json
    email = data.get("email")
    otp = data.get("otp")
    
    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400
        
    record = otps_col.find_one({"email": email})
    
    if not record:
        return jsonify({"error": "No OTP found for this email"}), 400
        
    # Check expiration (10 minutes)
    if (datetime.now() - record["created_at"]).total_seconds() > 600:
        return jsonify({"error": "OTP expired. Please request a new one."}), 400
        
    if record["otp"] == otp:
        otps_col.update_one({"email": email}, {"$set": {"verified": True}})
        return jsonify({"success": True, "message": "Email verified successfully"})
    else:
        return jsonify({"error": "Invalid OTP"}), 400

# ----------------------------------------------
#  USER REGISTRATION
# ----------------------------------------------
# ----------------------------------------------
#  USERNAME AVAILABILITY CHECK
# ----------------------------------------------
@app.route("/api/check-username", methods=["POST"])
def check_username():
    data = request.json
    username = data.get("username")
    
    if not username:
        return jsonify({"error": "Username is required"}), 400

    # Basic format check
    import re
    if not re.match(r'^[a-zA-Z0-9_.]+$', username):
         return jsonify({"available": False, "error": "Invalid characters"}), 200 # Return 200 so frontend can display message easily
    if len(username) < 3 or len(username) > 20:
         return jsonify({"available": False, "error": "Length must be 3-20 chars"}), 200

    # Check existence
    if users_col.find_one({"username": username}):
        # Generate suggestions
        import random
        suggestions = []
        base_username = username
        while len(suggestions) < 3:
            suffix = random.randint(10, 999)
            new_suggestion = f"{base_username}{suffix}"
            if not users_col.find_one({"username": new_suggestion}) and new_suggestion not in suggestions:
                suggestions.append(new_suggestion)
        
        return jsonify({
            "available": False,
            "message": "Username taken",
            "suggestions": suggestions
        })
    
    return jsonify({"available": True, "message": "Username available"})

# ----------------------------------------------
#  USER REGISTRATION
# ----------------------------------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name")
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    age = data.get("age")
    blood_group = data.get("bloodGroup")
    gender = data.get("gender")
    conditions = data.get("conditions", [])
    height = data.get("height")  # in cm
    weight = data.get("weight")  # in kg
    activity_level = data.get("activityLevel")

    # Required fields validation
    if not all([name, username, email, password, age, blood_group, gender, height, weight, activity_level]):
        return jsonify({"error": "All required fields must be filled"}), 400

    # Validate email format again (Backend enforcement)
    if not email.endswith("@gmail.com"):
        return jsonify({"error": "Only @gmail.com email addresses are allowed"}), 400

    # CHECK IF EMAIL IS VERIFIED
    otp_record = otps_col.find_one({"email": email})
    if not otp_record or not otp_record.get("verified"):
        return jsonify({"error": "Email not verified. Please verify your email first."}), 400

    # Username Validation Rules
    import re
    if not re.match(r'^[a-zA-Z0-9_.]+$', username):
        return jsonify({"error": "Username can only contain letters, numbers, underscores, and dots."}), 400
    if len(username) < 3 or len(username) > 20:
        return jsonify({"error": "Username must be between 3 and 20 characters."}), 400

    # Password Validation Rules
    def validate_password(pwd):
        if len(pwd) < 8:
            return "Password must be at least 8 characters long."
        if not re.search(r'[A-Z]', pwd):
            return "Password must contain at least one uppercase letter."
        if not re.search(r'[a-z]', pwd):
            return "Password must contain at least one lowercase letter."
        if not re.search(r'[0-9]', pwd):
            return "Password must contain at least one number."
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd):
            return "Password must contain at least one special character."
        return None

    password_error = validate_password(password)
    if password_error:
        return jsonify({"error": password_error}), 400

    # Check if username already exists
    if users_col.find_one({"username": username}):
        # Generate suggestions
        import random
        suggestions = []
        base_username = username
        while len(suggestions) < 3:
            suffix = random.randint(10, 999)
            new_suggestion = f"{base_username}{suffix}"
            if not users_col.find_one({"username": new_suggestion}) and new_suggestion not in suggestions:
                suggestions.append(new_suggestion)
        
        return jsonify({
            "error": f"Username '{username}' is already taken.",
            "suggestions": suggestions
        }), 400

    # Age validation (5 < age < 55)
    try:
        age_int = int(age)
        if age_int <= 5 or age_int >= 120:
             return jsonify({"error": "Age must be between 6 and 119"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid age format"}), 400

    # Height and weight validation
    try:
        height_cm = float(height)
        weight_kg = float(weight)
        if height_cm < 50 or height_cm > 250:
            return jsonify({"error": "Height must be between 50 and 250 cm"}), 400
        if weight_kg < 20 or weight_kg > 300:
            return jsonify({"error": "Weight must be between 20 and 300 kg"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid height or weight format"}), 400

    # Activity level validation
    valid_activity_levels = ["sedentary", "moderate", "active"]
    if activity_level not in valid_activity_levels:
        return jsonify({"error": "Invalid activity level"}), 400

    # Calculate BMI
    height_m = height_cm / 100
    bmi_val = weight_kg / (height_m ** 2)
    bmi = int(round(bmi_val))
    
    # Determine BMI category
    if bmi < 18.5:
        bmi_category = "underweight"
    elif bmi < 25:
        bmi_category = "normal"
    elif bmi < 30:
        bmi_category = "overweight"
    else:
        bmi_category = "obese"

    # Check if email already exists (Double check)
    if users_col.find_one({"email": email}):
        return jsonify({"error": "Email already exists"}), 400

    # Build user document
    # Separate predefined conditions from other conditions
    predefined_conditions = [c for c in conditions if c in ["bp", "diabetes"]]
    other_conditions = [c for c in conditions if c not in ["bp", "diabetes"]]
    
    user_doc = {
        "name": name,
        "username": username,
        "email": email,
        "password": password,
        "age": age_int,
        "blood_group": blood_group,
        "gender": gender,
        "conditions": predefined_conditions,
        "other_conditions": other_conditions if other_conditions else [],
        "height": height_cm,
        "weight": weight_kg,
        "bmi": bmi,
        "bmi_category": bmi_category,
        "activity_level": activity_level,
        "created_at": datetime.now()
    }

    # Add female-specific fields if gender is female
    if gender == "female":
        user_doc["recent_pregnancy"] = data.get("recentPregnancy", False)
        user_doc["pcod"] = data.get("pcod", False)

    users_col.insert_one(user_doc)
    
    # Clean up OTP record
    otps_col.delete_one({"email": email})

    return jsonify({"success": True, "message": "User registered successfully"})

# ----------------------------------------------
#  USER LOGIN
# ----------------------------------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = users_col.find_one({"email": email, "password": password})
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # Return user data (excluding password)
    user_data = {
        "name": user.get("name"),
        "email": user.get("email"),
        "age": user.get("age"),
        "blood_group": user.get("blood_group"),
        "gender": user.get("gender"),
        "conditions": user.get("conditions", []),
        "other_conditions": user.get("other_conditions", []),
        "height": user.get("height"),
        "weight": user.get("weight"),
        "bmi": user.get("bmi"),
        "bmi_category": user.get("bmi_category"),
        "activity_level": user.get("activity_level")
    }
    
    if user.get("gender") == "female":
        user_data["recent_pregnancy"] = user.get("recent_pregnancy", False)
        user_data["pcod"] = user.get("pcod", False)

    return jsonify({
        "success": True,
        "user": user_data
    })

# ----------------------------------------------
#  FORGOT PASSWORD & RESET (NEW)
# ----------------------------------------------
@app.route("/api/send-reset-otp", methods=["POST"])
def send_reset_otp():
    data = request.json
    email = data.get("email")
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    # Check if user exists (We can only reset password for existing users)
    if not users_col.find_one({"email": email}):
        return jsonify({"error": "Email not found. Please register first."}), 404
        
    otp = generate_otp()
    
    # Store OTP with timestamp
    otps_col.update_one(
        {"email": email},
        {"$set": {
            "otp": otp, 
            "created_at": datetime.now(),
            "verified": False
        }},
        upsert=True
    )
    
    # Send email (or print to console)
    if send_email_otp(email, otp):
        return jsonify({"success": True, "message": "OTP sent successfully"})
    else:
        return jsonify({"error": "Failed to send OTP"}), 500

@app.route("/api/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    email = data.get("email")
    otp = data.get("otp")
    new_password = data.get("newPassword")
    
    if not email or not otp or not new_password:
        return jsonify({"error": "Email, OTP, and new password are required"}), 400
        
    # Verify OTP
    record = otps_col.find_one({"email": email})
    if not record:
        return jsonify({"error": "No OTP request found"}), 400
        
    if (datetime.now() - record["created_at"]).total_seconds() > 600:
        return jsonify({"error": "OTP expired. Please request a new one."}), 400
        
    if record["otp"] != otp:
        return jsonify({"error": "Invalid OTP"}), 400
        
    # Update Password
    users_col.update_one(
        {"email": email},
        {"$set": {"password": new_password}}
    )
    
    # Clean up
    otps_col.delete_one({"email": email})
    
    return jsonify({"success": True, "message": "Password reset successfully. Please login."})

# ----------------------------------------------
#  GET USER PROFILE
# ----------------------------------------------
@app.route("/api/user/<email>", methods=["GET"])
def get_user_profile(email):
    try:
        user = users_col.find_one({"email": email})
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Return user data (excluding password)
        user_data = {
            "name": user.get("name"),
            "email": user.get("email"),
            "age": user.get("age"),
            "blood_group": user.get("blood_group"),
            "gender": user.get("gender"),
            "conditions": user.get("conditions", []),
            "other_conditions": user.get("other_conditions", []),
            "height": user.get("height"),
            "weight": user.get("weight"),
            "bmi": user.get("bmi"),
            "bmi_category": user.get("bmi_category"),
            "activity_level": user.get("activity_level")
        }
        
        if user.get("gender") == "female":
            user_data["recent_pregnancy"] = user.get("recent_pregnancy", False)
            user_data["pcod"] = user.get("pcod", False)

        return jsonify({"success": True, "user": user_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------------------------
#  RECOMMENDATION ROUTE (ML-Enhanced)
# ----------------------------------------------
@app.route("/api/recommend", methods=["POST"])
def recommend():
    try:
        data = request.json
        email = data.get("email")
        condition = data.get("condition")
        severity = data.get("severity")
        timeAvailable = data.get("timeAvailable")
        frequency = data.get("frequency")

        # Fetch user details from database
        user = users_col.find_one({"email": email})
        if not user:
            return jsonify({"error": "User not found. Please register first."}), 404

        # Use user's age from database
        age = user.get("age")
        gender = user.get("gender", "")
        conditions = user.get("conditions", [])
        
        print("Incoming:", condition, age, severity)
        print("User details:", {
            "age": age,
            "gender": gender,
            "conditions": conditions,
            "pcod": user.get("pcod", False) if gender == "female" else None,
            "recent_pregnancy": user.get("recent_pregnancy", False) if gender == "female" else None
        })

        # === TRY ML PREDICTION FIRST ===
        rec = None
        ml_used = False
        
        try:
            ml_rec_instance = get_ml_recommender()
            if ml_rec_instance:
                # Prepare user data for ML
                ml_user_data = {
                    'condition': condition,
                    'age': age,
                    'gender': gender,
                    'severity': severity,
                    'has_bp': 1 if 'bp' in conditions else 0,
                    'has_diabetes': 1 if 'diabetes' in conditions else 0,
                    'bmi_category': user.get('bmi_category', 'normal'),
                    'activity_level': user.get('activity_level', 'moderate'),
                    'time_available': int(timeAvailable) if timeAvailable else 30
                }
                
                # Get ML recommendation
                ml_rec = ml_rec_instance.get_recommendation(ml_user_data, confidence_threshold=0.3)
                
                if ml_rec:
                    rec = ml_rec
                    ml_used = True
                    print("✓ Using ML recommendation")
        except Exception as ml_error:
            print(f"ML prediction failed: {ml_error}")
            import traceback
            traceback.print_exc()

        # === FALLBACK TO RULE-BASED SYSTEM ===
        if not rec:
            print("→ Using rule-based fallback")
            # Build condition string considering user's stored conditions
            condition_str = condition
            if "bp" in conditions or "diabetes" in conditions:
                user_conditions = [c for c in conditions if c in ["bp", "diabetes"]]
                if user_conditions:
                    condition_str = f"{condition} with {', '.join(user_conditions)}"

            # Prepare parameters for matching
            has_bp = 1 if 'bp' in conditions else 0
            has_diabetes = 1 if 'diabetes' in conditions else 0
            
            rec = match_recommendation(
                dataset, 
                condition_str, 
                age, 
                severity,
                time_available=timeAvailable,
                gender=gender,
                activity_level=user.get('activity_level'),
                bmi_category=user.get('bmi_category'),
                has_bp=has_bp,
                has_diabetes=has_diabetes
            )
            if not rec:
                print("No match found in dataset, trying with base condition")
                rec = match_recommendation(
                    dataset, 
                    condition, 
                    age, 
                    severity,
                    time_available=timeAvailable,
                    gender=gender,
                    activity_level=user.get('activity_level'),
                    bmi_category=user.get('bmi_category'),
                    has_bp=has_bp,
                    has_diabetes=has_diabetes
                )
                if not rec:
                    print("No match found in dataset")
                    return jsonify({"error": "No recommendation found"}), 404

        # Check for unsafe poses based on conditions
        warning = None
        unsafe_poses = {
            "bp": ["shirshasana", "sarvangasana", "halasana", "kapalbhati", "adho_mukha_vrksasana", "chakrasana", "viparita_karani"],
            "diabetes": ["shirshasana", "sarvangasana"]
        }

        user_conditions_list = [c for c in conditions if c in ["bp", "diabetes"]]
        
        # Check if the recommended pose is unsafe
        pose_name = str(rec.get("yogapose", "")).lower()
        
        for cond in user_conditions_list:
            if cond in unsafe_poses:
                for unsafe in unsafe_poses[cond]:
                    if unsafe in pose_name:
                        if cond == "bp":
                             warning = f"⚠️ Caution: Avoid doing this yoga pose ({rec.get('yogapose', 'N/A')}) excessively as you have Blood Pressure."
                        else:
                             warning = f"⚠️ Caution: The recommended pose '{rec.get('yogapose', 'N/A')}' may not be suitable for people with {cond.upper()}. Please consult your doctor before performing this."
                        break
            if warning:
                break

        # Validate images
        IMAGES_DIR = os.path.join(os.path.dirname(__file__), "../frontend/images")
        
        def validate_image(img_name, default_img):
            if not img_name:
                return default_img
            
            # Check if file exists locally
            if os.path.exists(os.path.join(IMAGES_DIR, img_name)):
                return img_name
            
            # If not found locally, return the name anyway so frontend can generate it
            # We strip .jpg extension if present to make it cleaner for prompting, 
            # but for consistency with existing logic we can keep it or handle in frontend.
            # Let's keep it as is, frontend will handle the prompt generation.
            print(f"Image {img_name} not found locally, will use for dynamic generation")
            return img_name

        rec_record = {
            "email": str(email),
            "condition": str(condition),
            "age": int(age),
            "gender": gender,
            "user_conditions": conditions,
            "severity": str(severity),
            "yogapose": validate_image(rec.get("yogapose", rec.get("yoga_pose")), "shavasana.jpg"),
            "exercise": validate_image(rec.get("exercise"), "slow_walking.jpg"),
            "ayurveda_tip": validate_image(rec.get("ayurveda_tip"), "green_tea.jpg"),
            "timeAvailable": str(timeAvailable),
            "regularity": str(frequency),
            "created_at": datetime.now(),
            "warning": warning,
            "ml_used": ml_used,  # Track if ML was used
            "ml_confidence": rec.get("ml_confidence", 0) if ml_used else 0
        }

        # Add female-specific data if applicable
        if gender == "female":
            rec_record["pcod"] = user.get("pcod", False)
            rec_record["recent_pregnancy"] = user.get("recent_pregnancy", False)

        inserted = recs_col.insert_one(rec_record)
        rec_record["_id"] = str(inserted.inserted_id)

        print("Matched record:", rec_record)

        # Get steps for each item
        from steps_data import steps_data
        yoga_steps = steps_data.get(rec_record["yogapose"], ["Steps not available."])
        exercise_steps = steps_data.get(rec_record["exercise"], ["Steps not available."])
        ayurveda_steps = steps_data.get(rec_record["ayurveda_tip"], ["Steps not available."])

        return jsonify({
            "success": True, 
            "recommendation": rec_record,
            "steps": {
                "yoga": yoga_steps,
                "exercise": exercise_steps,
                "ayurveda": ayurveda_steps
            }
        })

    except Exception as e:
        print("Server error:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Server crashed", "details": str(e)}), 500

# ----------------------------------------------
#  USER HISTORY
# ----------------------------------------------
@app.route("/api/history/<email>", methods=["GET"])
def get_history(email):
    try:
        records = list(recs_col.find({"email": email}).sort("created_at", -1))
        for r in records:
            r["_id"] = str(r["_id"])
            if "created_at" in r:
                r["created_at"] = str(r["created_at"])
        return jsonify({"success": True, "records": records})
    except Exception as e:
        print("Error fetching history:", e)
        return jsonify({"success": False, "error": str(e)}), 500

# ----------------------------------------------
#  USER STATS (Streaks + Total Sessions)
# ----------------------------------------------
@app.route("/api/stats/<email>", methods=["GET"])
def get_user_stats(email):
    try:
        records = list(recs_col.find({"email": email}))
        if not records:
            return jsonify({
                "success": True,
                "current_streak": 0,
                "longest_streak": 0,
                "total_sessions": 0
            })

        # Convert to dates
        dates = sorted([
            r["created_at"].date() if isinstance(r["created_at"], datetime)
            else datetime.fromisoformat(str(r["created_at"])).date()
            for r in records
        ])

        total_sessions = len(dates)
        longest_streak = 1
        current_streak = 1
        streak = 1

        for i in range(1, len(dates)):
            diff = (dates[i] - dates[i - 1]).days
            if diff == 1:
                streak += 1
                longest_streak = max(longest_streak, streak)
            elif diff > 1:
                streak = 1

        if (datetime.now().date() - dates[-1]).days > 1:
            current_streak = 0
        else:
            current_streak = streak

        return jsonify({
            "success": True,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_sessions": total_sessions
        })

    except Exception as e:
        print("Error in stats:", e)
        return jsonify({"success": False, "error": str(e)}), 500

# ----------------------------------------------
#  GLOBAL CONDITION STATS (For Dashboard Graph)
# ----------------------------------------------
@app.route("/api/stats/conditions", methods=["GET"])
def get_condition_stats():
    try:
        # Aggregate all conditions from all users
        pipeline = [
            {"$project": {"conditions": 1, "other_conditions": 1, "pcod": 1, "recent_pregnancy": 1}},
            {"$unwind": {"path": "$conditions", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$other_conditions", "preserveNullAndEmptyArrays": True}}
        ]
        
        # We'll use a manual aggregation in python to be safer with the mixed schema
        users = list(users_col.find({}, {
            "conditions": 1, 
            "other_conditions": 1, 
            "pcod": 1, 
            "recent_pregnancy": 1, 
            "gender": 1
        }))
        
        stats = {}
        
        for user in users:
            # Process standard conditions (bp, diabetes)
            for c in user.get("conditions", []):
                if not c: continue
                name = c.replace("_", " ").title()
                # Map specific keys to nice names if needed
                if c == "bp": name = "Blood Pressure"
                if c == "diabetes": name = "Diabetes"
                stats[name] = stats.get(name, 0) + 1
                
            # Process other conditions
            for c in user.get("other_conditions", []):
                if not c: continue
                name = c.replace("_", " ").title()
                stats[name] = stats.get(name, 0) + 1
                
            # Process female specific
            if user.get("pcod"):
                stats["PCOS/PCOD"] = stats.get("PCOS/PCOD", 0) + 1
            if user.get("recent_pregnancy"):
                stats["Recent Pregnancy"] = stats.get("Recent Pregnancy", 0) + 1

        return jsonify({"success": True, "data": stats})

    except Exception as e:
        print("Error in condition stats:", e)
        return jsonify({"success": False, "error": str(e)}), 500

# ----------------------------------------------
#  CHATBOT ENDPOINT (Gemini API)
# ----------------------------------------------
@app.route("/api/chatbot", methods=["POST"])
def chatbot():
    try:
        # Initialize model for this request
        model = get_chatbot_model()
        if model is None:
            return jsonify({
                "success": False,
                "error": "Chatbot model not available. Please check API key and model availability."
            }), 500

        data = request.json
        user_message = data.get("message", "")
        email = data.get("email")
        conversation_history = data.get("conversation_history", [])
        language = data.get("language", "en") # Default to clean English

        # Map language codes to names for the prompt
        lang_names = {
            "en": "English",
            "te": "Telugu",
            "kn": "Kannada",
            "hi": "Hindi"
        }
        target_lang = lang_names.get(language, "English")

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Fetch user data from database if email provided
        user_context = ""
        if email:
            user = users_col.find_one({"email": email})
            if user:
                conditions = user.get("conditions", [])
                other_conditions = user.get("other_conditions", [])
                all_conditions = conditions + other_conditions
                
                user_context = f"""
Patient Background Information:
- Name: {user.get('name', 'Unknown')}
- Age: {user.get('age', 'Unknown')}
- Gender: {user.get('gender', 'Unknown')}
- Blood Group: {user.get('blood_group', 'Unknown')}
- Health Conditions: {', '.join(all_conditions) if all_conditions else 'None'}
"""
                
                if user.get("gender") == "female":
                    if user.get("recent_pregnancy", False):
                        user_context += "- Recent Pregnancy: Yes\n"
                    if user.get("pcod", False):
                        user_context += "- PCOS: Yes\n"

        # Fetch latest recommendation for context
        latest_rec = recs_col.find_one({"email": email}, sort=[("created_at", -1)])
        rec_context = ""
        if latest_rec:
            rec_context = f"""
Recent Health Recommendation (Date: {latest_rec.get('created_at', 'Unknown')}):
- Issue Reported: {latest_rec.get('condition', 'Unknown')} (Severity: {latest_rec.get('severity', 'Unknown')})
- Suggested Yoga: {latest_rec.get('yogapose', 'None')}
- Suggested Exercise: {latest_rec.get('exercise', 'None')}
- Ayurveda Tip: {latest_rec.get('ayurveda_tip', 'None')}
"""

        # Build the full prompt
        conversation_text = format_conversation_history(conversation_history) if conversation_history else "This is the start of the conversation."
        
        full_prompt = f"""You are a warm, energetic, and deeply caring Wellness Best Friend. You are not just an AI, but a supportive companion on the user's journey to better health.

{user_context}
{rec_context}

Your Personality & Approach:
1. **Be Super Friendly & Motivating**: Use emojis 🌿✨💪, warm greetings, and encouraging language. Be their cheerleader!
2. **Short & Sweet**: Respond in 1-2 lines MAX. Just like texting a friend. No paragraphs.
3. **Casual Tone**: Talk like a real friend. Relaxed and natural.
4. **Check-in**: If they mention their condition, ask how it's going.
5. **Empathetic**: Validate their feelings briefly.
6. **LANGUAGE**: You MUST reply in {target_lang}. Even if the user asks in English, if the target language is {target_lang}, reply in {target_lang}.

Previous conversation context:
{conversation_text}

User's current message: "{user_message}"

Now provide a warm, motivating, and personalized response in {target_lang} (keep it short!):"""

        print("Sending request to Gemini API...")
        
        # Generate response using Gemini with proper error handling
        try:
            # Use dictionary format for generation config (more compatible)
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
            
            response = model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            print("Gemini API response received")
            
            # Extract response text - handle different response structures
            response_text = None
            
            # Method 1: Direct text attribute (most common)
            try:
                if hasattr(response, 'text') and response.text:
                    response_text = response.text
            except:
                pass
            
            # Method 2: Access via candidates
            if not response_text:
                try:
                    if hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            if candidate.content.parts and len(candidate.content.parts) > 0:
                                response_text = candidate.content.parts[0].text
                        elif hasattr(candidate, 'text'):
                            response_text = candidate.text
                except Exception as e:
                    print(f"Error accessing candidates: {e}")
            
            # Method 3: Direct parts access
            if not response_text:
                try:
                    if hasattr(response, 'parts') and response.parts:
                        response_text = response.parts[0].text
                except Exception as e:
                    print(f"Error accessing parts: {e}")
            
            # Method 4: String representation fallback
            if not response_text:
                try:
                    response_str = str(response)
                    # Try to extract text from string representation
                    if 'text' in response_str.lower():
                        import re
                        match = re.search(r'text[:\s]+["\']?([^"\']+)["\']?', response_str, re.IGNORECASE)
                        if match:
                            response_text = match.group(1)
                except:
                    pass
            
            if response_text:
                cleaned_text = response_text.strip()
                print(f"Successfully extracted response: {cleaned_text[:100]}...")
                return jsonify({
                    "success": True,
                    "response": cleaned_text
                })
            else:
                print("ERROR: No text found in response")
                print(f"Response type: {type(response)}")
                print(f"Response attributes: {dir(response)}")
                print(f"Response string: {str(response)[:500]}")
                return jsonify({
                    "success": False,
                    "error": "Unable to extract response from API",
                    "debug": f"Response type: {type(response)}, Attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}"
                }), 500
                
        except Exception as api_error:
            print("Gemini API call error:", api_error)
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": f"API Error: {str(api_error)}"
            }), 500

    except Exception as e:
        print("Chatbot endpoint error:", e)
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "An error occurred while processing your message",
            "details": str(e)
        }), 500

def format_conversation_history(history):
    """Format conversation history for context"""
    if not history:
        return ""
    
    formatted = []
    for msg in history[-10:]:  # Last 10 messages
        role = "Patient" if msg.get("sender") == "user" else "Assistant"
        text = msg.get("text", "")
        formatted.append(f"{role}: {text}")
    
    return "\n".join(formatted)

# ----------------------------------------------
#  SERVER STATUS
# ----------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Wellness AI Backend Running ✅"})

# ----------------------------------------------
#  MAIN
# ----------------------------------------------
if __name__ == "__main__":
    print("🔥 Flask Server Running...")
    print("✅ Dataset loaded from:", DATA_PATH)
    print("🌐 Server running on: http://127.0.0.1:5001")
    app.run(debug=True, port=5001)  # Changed to port 5001 to avoid Windows conflict
