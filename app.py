from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel

import joblib
import os

# Model path from env if exists
model_path = os.getenv("CPA_MODEL_PATH", "resources/models/cpa_regressor.joblib")

# Load the model
model = joblib.load(model_path)

# Start the app
app = FastAPI()

# The input structure
class InputData(BaseModel):
    category_id: str
    industry: str
    customer_id: str
    publisher: str
    market_id: str
    CPC: float

# A quick health check
@app.get("/")
def health_check():
    return {"status": "OK"}


@app.post("/predict")
def predict(data: InputData):
    # Get the data from the post call and turn it into a dataframe
    input_data = pd.DataFrame([data.model_dump()])

    # Predict 
    prediction = model.predict(input_data)

    # Return the prediction
    return {"CPA_prediction": float(prediction[0])}
