


import argparse
from pathlib import Path

import joblib
import pandas as pd


def load_model(path: Path):
    """Loads the model

    Args:
        path (Path): The model path

    Returns:
        sklearn.pipeline: The sklearn fitted pipeline
    """
    return joblib.load(path)

def predict(model, X: pd.DataFrame):
    """Predicts a dataframe fro a trained model

    Args:
        model (sklearn.pipeline): A trained model
        X (pd.DataFrame): The dataframe to predict

    Returns:
        np.array: The prediction results
    """
    return model.predict(X)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Predict a csv based on a trained model."
    )
    parser.add_argument(
        "--model-path",
        type=str,
        required=True,
        help="Path to the model.",
    )
    parser.add_argument(
        "--predict-csv-path",
        type=str,
        required=True,
        help="A csv with data for prediction.",
    )

    args = parser.parse_args()

    # loads the model
    model = load_model(Path(args.model_path))

    # gets the csv for prediction
    to_predict = pd.read_csv(
        args.predict_csv_path,
        dtype={
        "category_id": str,
        "industry": str,
        "customer_id": str,
        "publisher": str, 
        "market_id": str,
        "CPC": float
    },
    )

    # predicts
    predictions = predict(model, to_predict)

    # adds predictions dataframe
    to_predict["CPA_prediction"] = predictions

    print(to_predict)
