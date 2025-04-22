import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from xgboost import XGBRegressor

from sklearn.preprocessing import TargetEncoder, OneHotEncoder
import joblib
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def save_model(model: XGBRegressor, model_path: Path):
    joblib.dump(model, model_path)


def train(input_data_path: Path, output_model_path: Path):
    # Reading data
    # Parse date and all ids should be as string mainly because it's safer for ids to be strings. Besides, we want to treat these
    # as categorical features
    logging.info("Reading data...")
    df = pd.read_csv(
        input_data_path,
        dtype={
            "campaign_id": str,
            "category_id": str,
            "industry": str,
            "customer_id": str,
            "publisher": str,  # hexadecimal number, but str suits our purposes.
            "market_id": str,
            "cost": float,
            "clicks": float,  # Should be integer but cannot safely convert. We round and convert later
            "converions": int,
        },
        parse_dates=["date"],
    )

    logging.info("Preprocessing...")
    # Rename due to typo
    df.rename(columns={"converions": "conversions"}, inplace=True)

    # Convert clicks to integer
    df["clicks"] = df["clicks"].round().astype(int)

    # Remove bad data
    df = df[df.conversions < df.clicks]  # More conversions than clicks is not possible

    df = (
        df.groupby(
            [
                "campaign_id",
                "category_id",
                "industry",
                "customer_id",
                "publisher",
                "market_id",
            ]
        )
        .agg({"cost": "sum", "clicks": "sum", "conversions": "sum"})
        .reset_index()
    )

    # If conversions is zero, then CPC = Cost
    df["CPC"] = df.apply(lambda x: x["cost"] if x["conversions"] == 0 else x["cost"] / x["conversions"] ,axis=1) 

    # If conversions is zero, then CPA = Cost
    df["CPA"] = df.apply(lambda x: x["cost"] if x["clicks"]==0 else x["cost"] / x["clicks"], axis=1)

    df["CPA_transformed"] = np.log1p(df["CPA"])

    onehot_cols = ["category_id", "industry", "customer_id", "publisher"]
    target_encoder_cols = ["market_id"]
    num_cols = ["CPC"]

    training_cols = onehot_cols + target_encoder_cols + num_cols
    label = ["CPA_transformed"]
    all_cols = training_cols + label

    df_dedupl = df[all_cols].drop_duplicates()

    X = df_dedupl[training_cols]
    y = df_dedupl[label].CPA_transformed.values

    logging.info("Starting to train...")
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "Medium-Low Cardinality Categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                onehot_cols,
            ),
            ("High Cardinality Categorical", TargetEncoder(), target_encoder_cols),
            (
                "Numerical",
                "passthrough",
                num_cols,
            ),  # XGBoost already deals with numerical well
        ]
    )

    regressor = XGBRegressor(
        objective='reg:squarederror',
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )

    pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", regressor)])

    pipeline.fit(X, y)

    logging.info("Saving Model...")
    save_model(model=pipeline, model_path=output_model_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train a model with input data and save the output model."
    )
    parser.add_argument(
        "--input_data_path",
        type=str,
        default="resources/data/ds_challenge_data.csv",
        help="Path to the input data.",
    )
    parser.add_argument(
        "--output_model_path",
        type=str,
        default="resources/models/cpa_regressor.joblib",
        help="Path to save the trained model.",
    )

    args = parser.parse_args()

    train(Path(args.input_data_path), Path(args.output_model_path))
