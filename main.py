from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import ALLOWED_ORIGINS
from database import engine, SessionLocal
from models import Base, UserData, StressData
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
import joblib
import numpy as np

app = FastAPI()

Base.metadata.create_all(bind=engine)

class SignupRequest(BaseModel):
    email: str
    password: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Backend Running"}

@app.post("/signup")
def signup(user: SignupRequest):
    db = SessionLocal()

    try:
        new_user = UserData(
            email=user.email,
            password=user.password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User Saved",
            "id": new_user.id
        }

    except IntegrityError:
        db.rollback()
        return {
            "error": "Email already exists"
        }

    finally:
        db.close()



class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/login")
def login(user: LoginRequest):
    db = SessionLocal()

    try:
        # Step 1: find user by email
        db_user = db.query(UserData).filter(UserData.email == user.email).first()

        # Step 2: check if user exists
        if not db_user:
            return {
                "success": False,
                "message": "Invalid credentials"
            }

        # Step 3: check password
        if db_user.password != user.password:
            return {
                "success": False,
                "message": "Invalid credentials"
            }

        return {
            "success": True,
            "message": "Login successful",
            "user_id": db_user.id
        }

    finally:
        db.close()

class StressRequest(BaseModel):
    email: str 
    sleep: float
    work: float
    mood: float
    screen: float
    activity: float
    heart: float
    spo2: float

model = joblib.load("stress_model.pkl")
encoder = joblib.load("label_encoder.pkl")

@app.post("/predict-stress")
def predict_stress(data: StressRequest):
    db = SessionLocal()

    try:
        # ML input
        features = np.array([[
            data.sleep,
            data.work,
            data.mood,
            data.screen,
            data.activity,
            data.heart,
            data.spo2
        ]])

        # Prediction
        prediction = model.predict(features)
        result = encoder.inverse_transform(prediction)[0]

        # Get user
        user = db.query(UserData).filter(UserData.email == data.email).first()

        if not user:
            return {
                "success": False,
                "message": "User not found"
            }

        # Save into DB (INCLUDING RESULT)
        new_record = StressData(
            user_id=user.id,
            
            sleep=data.sleep,
            work=data.work,
            mood=data.mood,
            screen=data.screen,
            activity=data.activity,
            heart=data.heart,
            spo2=data.spo2,
            prediction=result   
        )

        db.add(new_record)
        db.commit()

        return {
            "success": True,
            "stressLevel": result
        }

    except Exception as e:
        db.rollback()
        print("ERROR:", e)
        return {
        "success": False,
        "message": str(e)
    }
    finally:
        db.close()


@app.get("/history")
def get_history(email: str):
    db = SessionLocal()
    try:
        user = db.query(UserData).filter(UserData.email == email).first()

        if not user:
            return {"success": False, "message": "User not found"}

        records = db.query(StressData).filter(StressData.user_id == user.id).all()

        return {
            "success": True,
            "records": [
                {
                    "sleep": r.sleep,
                    "work": r.work,
                    "mood": r.mood,
                    "screen": r.screen,
                    "activity": r.activity,
                    "heart": r.heart,
                    "spo2": r.spo2,
                    "prediction": r.prediction,
                    "date":r.timestamp
                }
                for r in records
            ]
        }

    finally:
        db.close()