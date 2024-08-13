import logging
import pandas as pd
import numpy as np
import my_config

# Initialize the logger
logger = logging.getLogger(__name__)

def clear_data(file_path):
    logger.info('Starting data cleaning process.')
    
    # Load data from CSV file
    try:
        df = pd.read_csv(file_path)
        logger.info('Data successfully loaded from %s', file_path)
    except Exception as e:
        logger.error('Failed to load data from %s: %s', file_path, str(e))
        return None
    
    # Clean and convert item price
    df['item_price'] = df['item_price'].str.replace('₽', '').str.replace('\xa0', '')
    df['item_price'] = pd.to_numeric(df['item_price'], errors='coerce')
    df['item_price'] = df['item_price'].fillna(0).astype(int)
    logger.info('Item price cleaned and converted.')

    # Convert product rating and review count to numeric values
    df['item_product_rating'] = pd.to_numeric(df['item_product_rating'], errors='coerce')
    df['item_count_reviews'] = pd.to_numeric(df['item_count_reviews'], errors='coerce')
    logger.info('Product rating and review count converted to numeric values.')
    
    # Capitalize the first letter of item names
    df['item_name'] = df['item_name'].str.capitalize()
    logger.info('Item names capitalized.')

    # Handle missing image URLs
    df['item_image'] = df['item_image'].replace("", np.nan)
    df['item_image'].fillna("None", inplace=True)
    logger.info('Missing image URLs handled.')

    # Fill remaining NaN values with the mean of each column
    df.fillna(df.mean(numeric_only=True), inplace=True)
    logger.info('Remaining NaN values filled with column means.')

    logger.info('Data cleaning process completed.')
    return df

def feature_engineering(df):
    logger.info('Starting feature engineering process.')
    
    # Calculate average price by brand and discount
    avg_price_by_brand = df.groupby('item_company_name')['item_price'].transform('mean')
    df['discount'] = avg_price_by_brand - df['item_price']
    df['discount'] = df['discount'].round(4)
    logger.info('Discount calculated based on average price by brand.')

    # Calculate reviews to rating ratio
    df['reviews_to_rating_ratio'] = df['item_count_reviews'] / df['item_product_rating']
    df['reviews_to_rating_ratio'] = df['reviews_to_rating_ratio'].round(4)
    logger.info('Reviews to rating ratio calculated.')

    # Categorize rating into low, medium, and high
    df['rating_category'] = pd.cut(df['item_product_rating'], bins=[0, 3, 4, 5], labels=['low', 'medium', 'high'])
    logger.info('Rating category assigned.')

    # Perform One-Hot Encoding on the brand column
    df_encoded = pd.get_dummies(df['item_company_name'], prefix='brand', drop_first=True)
    df_encoded.to_csv('brand_one_hot_encoded.csv', index=False)
    logger.info('One-Hot Encoding performed on brand column and saved to "brand_one_hot_encoded.csv".')

    # Rename columns for clarity
    new_column_name = {
        'item_url': 'url',
        'item_price': 'price',
        'item_name': 'name',
        'item_company_name': 'brand',
        'item_image': 'image'
    }
    df = df.rename(columns=new_column_name)
    logger.info('Columns renamed for clarity.')

    # Save the DataFrame to a Parquet file
    df.to_parquet('processed_data.parquet', index=False)
    logger.info('Data saved to "processed_data.parquet".')

    # Load the Parquet file to verify its contents
    df_loaded = pd.read_parquet('processed_data.parquet')
    logger.info('Data successfully loaded from "processed_data.parquet".')
    print(df_loaded.head())  # Display the first few rows for verification

    # Save the final DataFrame to a CSV file after feature engineering
    df.to_csv('final_data_after_feature.csv', index=False)
    logger.info('Final data saved to "final_data_after_feature.csv".')

    logger.info('Feature engineering process completed.')
    return df

# Example usage:
# Example usage:
if __name__ == '__main__':
    logger.info('Script started.')
    cleaned_df = clear_data('result.csv')
    if cleaned_df is not None:
        feature_df = feature_engineering(cleaned_df)
    logger.info('Script finished.')