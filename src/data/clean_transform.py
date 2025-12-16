import boto3
import pandas as pd
import io
from sklearn.preprocessing import LabelEncoder

# CONFIGURATION
BUCKET_NAME = "s3-gXmgXX"  # REPLACE WITH YOUR GROUP ID
S3_KEY_RAW = "raw/sleep_data.csv"
S3_KEY_CLEAN = "processed/sleep_data_clean.csv"

def clean_data():
    s3 = boto3.client("s3")
    
    print(f"Downloading {S3_KEY_RAW} from {BUCKET_NAME}...")
    try:
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=S3_KEY_RAW)
        df = pd.read_csv(io.BytesIO(obj["Body"].read()))
    except Exception as e:
        print(f"Error reading from S3: {e}")
        return

    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("/", "_")
    
    # Handle Blood Pressure "126/83"
    if 'blood_pressure' in df.columns:
        print("Splitting Blood Pressure column...")
        df[['systolic_bp', 'diastolic_bp']] = df['blood_pressure'].str.split('/', expand=True)
        df['systolic_bp'] = pd.to_numeric(df['systolic_bp'])
        df['diastolic_bp'] = pd.to_numeric(df['diastolic_bp'])
        df = df.drop(columns=['blood_pressure'])

    # Target Variable
    # In this dataset, NaN in 'sleep_disorder' means 'None' (Healthy)
    if 'sleep_disorder' in df.columns:
        df['sleep_disorder'] = df['sleep_disorder'].fillna('None')

    # ENCODING CATEGORICAL COLUMNS
    categorical_cols = ['gender', 'occupation', 'bmi_category', 'sleep_disorder']
    
    if 'bmi_category' in df.columns:
        df['bmi_category'] = df['bmi_category'].replace('Normal Weight', 'Normal')

    le = LabelEncoder()
    for col in categorical_cols:
        if col in df.columns:
            df[col] = le.fit_transform(df[col].astype(str))
            print(f"Encoded {col}")

    # 6. SAVE PROCESSED DATA
    print(f"Data shape after cleaning: {df.shape}")
    print("Uploading processed data to S3...")
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    s3.put_object(Bucket=BUCKET_NAME, Key=S3_KEY_CLEAN, Body=csv_buffer.getvalue())
    print("ETL Pipeline finished successfully.")

if __name__ == "__main__":
    clean_data()