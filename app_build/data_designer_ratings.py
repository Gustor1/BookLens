# /// script
# dependencies = [
#   "data-designer",
#   "pandas",
#   "numpy"
# ]
# ///
import data_designer.config as dd
import pandas as pd
import numpy as np
import os

# Load references once at module level for the generator
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOKS_PATH = os.path.join(BASE_DIR, "data", "raw", "Books.csv")
USERS_PATH = os.path.join(BASE_DIR, "data", "raw", "Users.csv")

try:
    books_df = pd.read_csv(BOOKS_PATH, sep=";")
    isbns = books_df["ISBN"].unique().tolist()
except Exception:
    isbns = ["0000000000"]

try:
    users_df = pd.read_csv(USERS_PATH, sep=";")
    user_ids = users_df["User-ID"].unique().tolist()
except Exception:
    user_ids = ["unknown-user"]

@dd.custom_column_generator(
    required_columns=["base_rating"],
    side_effect_columns=["User-ID", "ISBN", "Book-Rating"],
)
def generate_realistic_rating(row: dict) -> dict:
    """Generate a rating using the base Gaussian sample, bound it 1-10, and assign a random user and book."""
    import random
    
    # Randomly select user and book
    row["User-ID"] = random.choice(user_ids)
    row["ISBN"] = random.choice(isbns)
    
    # 20% chance of implicit rating (0)
    if random.random() < 0.20:
        row["Book-Rating"] = 0
    else:
        # Use the base Gaussian rating (centered around 7.5, std 1.5) and bound to 1-10
        base_val = row["base_rating"]
        rating = int(round(base_val))
        rating = max(1, min(10, rating))
        row["Book-Rating"] = rating
        
    row["rating_fields"] = True
    return row

def load_config_builder() -> dd.DataDesignerConfigBuilder:
    config_builder = dd.DataDesignerConfigBuilder()

    # Generate a gaussian distribution for the base rating
    config_builder.add_column(
        dd.SamplerColumnConfig(
            name="base_rating",
            sampler_type=dd.SamplerType.GAUSSIAN,
            params=dd.GaussianSamplerParams(
                mean=7.5,
                stddev=1.5
            ),
            drop=True
        )
    )

    config_builder.add_column(
        dd.CustomColumnConfig(
            name="rating_fields",
            generator_function=generate_realistic_rating
        )
    )

    return config_builder
