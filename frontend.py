import streamlit as st
import requests
import json

# CONFIGURATION
API_URL = "https://6ixeyncmu8.eu-west-3.awsapprunner.com/"

st.title("😴 Sleep Disorder Prediction System")
st.write("Enter patient details below to predict Sleep Apnea or Insomnia.")

# 1. Input Form
with st.form("prediction_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        gender = st.selectbox("Gender", ["Male", "Female"])
        age = st.number_input("Age", 10, 90, 30)
        occupation = st.selectbox("Occupation", ["Engineer", "Doctor", "Nurse", "Teacher", "Accountant", "Other"])
        sleep_duration = st.slider("Sleep Duration (hours)", 4.0, 10.0, 7.0, 0.1)
        quality_of_sleep = st.slider("Quality of Sleep (1-10)", 1, 10, 7)
        physical_activity = st.slider("Physical Activity (min/day)", 0, 120, 40)
    
    with col2:
        stress_level = st.slider("Stress Level (1-10)", 1, 10, 5)
        bmi = st.selectbox("BMI Category", ["Normal", "Overweight", "Obese"])
        heart_rate = st.number_input("Heart Rate (bpm)", 50, 120, 70)
        daily_steps = st.number_input("Daily Steps", 1000, 20000, 8000)
        systolic_bp = st.number_input("Systolic BP", 90, 180, 120)
        diastolic_bp = st.number_input("Diastolic BP", 60, 120, 80)
    
    submit = st.form_submit_button("Predict Disorder")

# 2. Logic
if submit:
    payload = {
        "gender": gender,
        "age": age,
        "occupation": occupation,
        "sleep_duration": sleep_duration,
        "quality_of_sleep": quality_of_sleep,
        "physical_activity_level": physical_activity,
        "stress_level": stress_level,
        "bmi_category": bmi,
        "heart_rate": heart_rate,
        "daily_steps": daily_steps,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp
    }
    
    with st.spinner("Asking the AI model..."):
        try:
            response = requests.post(f"{API_URL}/predict", json=payload)
            if response.status_code == 200:
                result = response.json()
                label = result.get("prediction_label", "Error")
                
                # Display Result
                if label == "None (Healthy)":
                    st.success(f"Diagnosis: {label} ✅")
                else:
                    st.error(f"Diagnosis: {label} ⚠️")
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Connection failed: {e}")

# 3. Sidebar for MLOps Actions
st.sidebar.header("MLOps Controls")

if st.sidebar.button("📊 View Model Metrics"):
    try:
        res = requests.get(f"{API_URL}/metrics")
        st.sidebar.json(res.json())
    except:
        st.sidebar.error("Could not fetch metrics")

if st.sidebar.button("🔄 Retrain Model"):
    try:
        res = requests.post(f"{API_URL}/train")
        st.sidebar.success(res.json()["message"])
    except:
        st.sidebar.error("Retraining failed trigger")