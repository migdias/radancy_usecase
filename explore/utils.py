from pathlib import Path
import pandas as pd

def read_historical_data(data_path: Path | str) -> pd.DataFrame:
    df = pd.read_csv(
            "../resources/data/ds_challenge_data.csv",
            dtype={
                "campaign_id": str,
                "category_id": str,
                "industry": str,
                "customer_id": str,
                "publisher": str, # hexadecimal number, but str suits our purposes.
                "market_id": str,
                "cost": float,
                "clicks": float, # Should be integer but cannot safely convert. We round and convert later
                "converions": int
            },
            parse_dates=["date"]
        )

    # Rename due to typo
    df.rename(columns={"converions": "conversions"}, inplace=True)

    # Convert clicks to integer
    df["clicks"] = df["clicks"].round().astype(int)

    return df