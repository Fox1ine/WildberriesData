# Wildberries Scraper

This project is a web scraping tool designed to extract product data from Wildberries.ru using Selenium and BeautifulSoup. The tool also includes data cleaning and feature engineering functions to process and analyze the scraped data.

## Features

- **Data Extraction:** Scrapes product information from Wildberries.ru, including name, brand, price, rating, review count, and image URLs.
- **Feature Engineering:** Calculates additional features such as discounts and reviews-to-rating ratios, and categorizes ratings.Cleans and formats the extracted data, including converting prices and ratings to numeric values, handling missing data, and capitalizing product names.
- **Output Data:** Raw scraped data saved as a CSV file. Cleaned and processed data saved as a Parquet file. One-hot encoded brand data.

