import boto3
import pandas as pd
import io
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

# CONFIGURATION
BUCKET_NAME = "s3-g1mg06"
S3_KEY_DATA = "processed/sleep_data_clean.csv"
S3_KEY_MODEL = "models/model.joblib"
LOCAL_MODEL_PATH = "models/model.joblib"

def train():
    s3 = boto3.client("s3")

    print("Loading data from S3")
    try:
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=S3_KEY_DATA)
        df = pd.read_csv(io.BytesIO(obj["Body"].read()))
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # PREPARE FEATURES & TARGET
    # 'sleep_disorder' is our target. Drop 'person_id' (it's not a feature)
    if 'person_id' in df.columns:
        df = df.drop(columns=['person_id'])
    
    X = df.drop(columns=['sleep_disorder'])
    y = df['sleep_disorder']

    # Split 80/20
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # TRAIN MODEL
    print("Training Random Forest Model")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    # SAVE ARTIFACTS
    os.makedirs("models", exist_ok=True)
    
    print(f"Saving model locally to {LOCAL_MODEL_PATH}")
    joblib.dump(model, LOCAL_MODEL_PATH)

    # UPLOAD TO S3
    print(f"Uploading model to s3://{BUCKET_NAME}/{S3_KEY_MODEL}")
    s3.upload_file(LOCAL_MODEL_PATH, BUCKET_NAME, S3_KEY_MODEL)
    print("Training pipeline finished successfully.")

if __name__ == "__main__":
    train()