from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from src.api.model_loader import load_model

from fastapi import BackgroundTasks
from src.model.train_model import train # Import your training function

app = FastAPI(title="Sleep Disorder Prediction API", version="1.0")

model = load_model()

class SleepInput(BaseModel):
    gender: str                 # "Male", "Female"
    age: int
    occupation: str             # "Nurse", "Doctor", etc.
    sleep_duration: float
    quality_of_sleep: int       # 1-10
    physical_activity_level: int
    stress_level: int           # 1-10
    bmi_category: str           # "Normal", "Overweight"
    heart_rate: int
    daily_steps: int
    systolic_bp: int            # Split from Blood Pressure
    diastolic_bp: int           # Split from Blood Pressure

# Preprocessing Helper
def preprocess_input(data: SleepInput):
    df = pd.DataFrame([data.dict()])
    
    df['gender'] = df['gender'].map({'Male': 1, 'Female': 0}).fillna(1)
    
    bmi_mapping = {'Normal': 0, 'Normal Weight': 0, 'Obese': 1, 'Overweight': 2}
    df['bmi_category'] = df['bmi_category'].map(bmi_mapping).fillna(0)
    
    df['occupation'] = 0 
    
    expected_cols = [
        'gender', 'age', 'occupation', 'sleep_duration', 'quality_of_sleep',
        'physical_activity_level', 'stress_level', 'bmi_category', 'heart_rate',
        'daily_steps', 'systolic_bp', 'diastolic_bp'
    ]
    return df[expected_cols]

# 3. Endpoints

@app.get("/health")
def health_check():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model_loaded": True}

@app.get("/metrics")
def get_metrics():
    s3 = boto3.client("s3")
    BUCKET_NAME = "s3-g1mg06" 

    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key="models/metrics.json")
        metrics_data = json.loads(response["Body"].read())
        return metrics_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Metrics not found: {str(e)}")

@app.post("/train")
def trigger_training(background_tasks: BackgroundTasks):
    background_tasks.add_task(train)
    
    return {
        "message": "Training started in the background. Check /metrics in a few minutes for updated results.",
        "status": "processing"
    }

@app.post("/predict")
def predict(input_data: SleepInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Model service unavailable")
    
    try:
        X = preprocess_input(input_data)
        
        prediction_index = model.predict(X)[0]
        
        # Map number back to text
        class_mapping = {
            0: "Insomnia",
            1: "None (Healthy)",
            2: "Sleep Apnea"
        }
        
        predicted_condition = class_mapping.get(int(prediction_index), "Unknown")
        
        return {
            "prediction_code": int(prediction_index),
            "prediction_label": predicted_condition
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))