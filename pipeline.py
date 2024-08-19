import logging
import os
import pandas as pd
import numpy as np

# Initialize the logger
logger = logging.getLogger(__name__)

def clear_data(file_path):
    """
    Load and clean data from a CSV file.

    """
    logger.info('Starting data cleaning process.')
    
    # Load data from CSV file
    try:
        df = pd.read_csv(file_path)
        logger.info('Data successfully loaded from %s', file_path)
    except Exception as e:
        logger.error('Failed to load data from %s: %s', file_path, str(e))
        return None
    
    # Clean and convert item price
    df['price'] = df['price'].str.replace('₽', '').str.replace('\xa0', '')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['price'] = df['price'].fillna(0).astype(int)
    logger.info('Item price cleaned and converted.')

    # Convert product rating and review count to numeric values
    df['product_rating'] = pd.to_numeric(df['product_rating'], errors='coerce')
    df['count_reviews'] = pd.to_numeric(df['count_reviews'], errors='coerce')
    logger.info('Product rating and review count converted to numeric values.')
    
    # Capitalize the first letter of item names
    df['name'] = df['name'].str.capitalize()
    logger.info('Item names capitalized.')

    # Handle missing image URLs
    df['image'] = df['image'].replace("", np.nan)
    df['image'].fillna("None", inplace=True)
    logger.info('Missing image URLs handled.')

    # Fill remaining NaN values with the mean of each column
    df.fillna(df.mean(numeric_only=True), inplace=True)
    logger.info('Remaining NaN values filled with column means.')

    logger.info('Data cleaning process completed.')
    return df

def feature_engineering(df):
    """
    Perform feature engineering on the DataFrame.

    """
    logger.info('Starting feature engineering process.')
    
    # Calculate average price by brand and discount
    avg_price_by_brand = df.groupby('brand')['price'].transform('mean')
    df['discount'] = avg_price_by_brand - df['price']
    df['discount'] = df['discount'].round(4)
    logger.info('Discount calculated based on average price by brand.')

    # Calculate reviews to rating ratio
    df['reviews_to_rating_ratio'] = df['count_reviews'] / df['product_rating']
    df['reviews_to_rating_ratio'] = df['reviews_to_rating_ratio'].round(4)
    logger.info('Reviews to rating ratio calculated.')

    # Categorize rating into low, medium, and high
    df['rating_category'] = pd.cut(df['product_rating'], bins=[0, 3, 4, 5], labels=['low', 'medium', 'high'])
    logger.info('Rating category assigned.')

    # Rename columns for clarity
    df = df.rename(columns={'company_name': 'brand'})
    logger.info('Columns renamed for clarity.')

    # Perform One-Hot Encoding on the brand column
    df_encoded = pd.get_dummies(df['brand'], prefix='brand', drop_first=True)
    df_encoded.to_csv('brand_one_hot_encoded.csv', index=False)
    logger.info('One-Hot Encoding performed on brand column and saved to "brand_one_hot_encoded.csv".')

    # Save the DataFrame to a Parquet file
    df.to_parquet('processed_data.parquet', index=False)
    if os.path.exists('./processed_data.parquet'):
        logger.info('Data saved to "processed_data.parquet".')
    else:
        logger.error("Something went wrong, file 'processed_data.parquet' was not created.")
    
    # Save the final DataFrame to a CSV file after feature engineering
    df.to_csv('final_data_after_feature.csv', index=False)
    logger.info('Final data saved to "final_data_after_feature.csv".')

    logger.info('Feature engineering process completed.')
    return df
