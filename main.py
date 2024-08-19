import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
from config import SELENIUM_EXPLICIT_WAIT, headers, service, options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pipeline import clear_data,feature_engineering


# Initialize the logger
logger = logging.getLogger(__name__)

def logger_value(value, message_if_exist, message_if_not_exist):
    if value:
        logger.info(message_if_exist)
    else:
        logger.warning(message_if_not_exist)


#Wait until the specified element is visible on the page.
def sleep_until_visible(driver, locator):
    """Wait until the specified element is visible."""
    return WebDriverWait(driver, SELENIUM_EXPLICIT_WAIT).until(
        EC.visibility_of_element_located(locator)
    )


def get_content(url):
    """Retrieve the HTML content of the given URL."""
    try:
        with webdriver.Firefox(service=service, options=options) as driver:
            driver.get(url)
            sleep_until_visible(driver, (By.CLASS_NAME, 'product-card__wrapper'))

            page_source = driver.page_source
            logger.info("HTML content successfully loaded")
            return page_source

    except Exception as err:
        logger.error(f"Something went wrong: {err}")
        return None


def extract_item_data(soup, tag, class_name, multiple=False, get_attr=None):
    """Extract data from a BeautifulSoup object based on the provided tag and class name."""
    if multiple:
        items = soup.findAll(tag, class_=class_name)
        if get_attr:
            return [item.get(get_attr) for item in items]
        return [item.get_text(strip=True) for item in items]
    
    item = soup.find(tag, class_=class_name)
    if item:
        if get_attr:
            return item.get(get_attr)
        return item.get_text(strip=True)
    return None


def get_item_urls(html_content):
    """Extract product URLs from the HTML content."""
    soup = BeautifulSoup(html_content, 'lxml')
    item_divs = soup.findAll('div', class_='product-card__wrapper')

    urls = []
    for i, div in enumerate(item_divs):
        if i >= 50:  # Modify the limit as needed
            break
        link = extract_item_data(div, "a", 'product-card__link j-card-link j-open-full-product-card', get_attr='href')
        if link and link.startswith('/'):
            link = f"https://www.wildberries.ru{link}"
        urls.append(link)

    logger.info("URLs collected successfully")
    return urls


def get_data(urls_list):
    """Retrieve data from the list of product URLs."""
    with webdriver.Firefox(service=service, options=options) as driver:
        result_list = []

        for url in urls_list:
            driver.get(url)
            sleep_until_visible(driver, (By.CLASS_NAME, 'product-page__title'))
            soup = BeautifulSoup(driver.page_source, 'lxml')

            try:
                item_name = extract_item_data(soup, 'h1', "product-page__title")
                logger_value(item_name,'item name collected successfully', 'item name collected UNsuccessfully')
                
                item_company_name = extract_item_data(soup, 'a', 'product-page__header-brand j-wba-card-item j-wba-card-item-show j-wba-card-item-observe')
                logger_value(item_company_name,'company name collected successfully','company name collected UNsuccessfully')

                item_product_rating = extract_item_data(soup, 'span', "product-review__rating address-rate-mini address-rate-mini--sm")
                logger_value(item_product_rating,'data product rating collected successfully','data product rating collected UNsuccessfully')

                item_count_reviews = extract_item_data(soup, 'span', 'product-review__count-review j-wba-card-item-show j-wba-card-item-observe')
                logger_value(item_count_reviews, 'data quantity reviews collected successfully','data quantity reviews collected UNsuccessfully')

                item_price = extract_item_data(soup, 'ins', "price-block__final-price wallet")
                logger_value(item_price,'data item price collected successfully','data item price collected UNsuccessfully')

                images_urls = extract_item_data(soup, 'img', 'photo-zoom__preview j-zoom-image hide', multiple=True, get_attr='src')
                logger_value(images_urls, 'data images_urls collected successfully', 'data images_urls collected UNsuccessfully')

                result_list.append(
                    {
                        'url': url,
                        'name': item_name,
                        'company_name': item_company_name,
                        'product_rating': item_product_rating,
                        'count_reviews': item_count_reviews,
                        'price': item_price,
                        'image': images_urls[0] if images_urls else None
                    }
                )

            except Exception as err:
                logger.error(f"Error processing {url}: {err}")

        # Save to CSV
        df = pd.DataFrame(result_list)
        df.to_csv("result.csv", index=False, encoding='utf-8', quoting=1) 
        if os.path.exists("./result.csv"):  
            logger.info("Data successfully saved to 'result.csv'")
        else:
            logger.error("File 'result.csv' was not created after saving attempt")

    


def parse_connect(user_value: str):
    """Parse product URLs based on user input."""
    url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={user_value}"
    html_content = get_content(url)
    urls = get_item_urls(html_content)
    return urls


def main():
    """Main function to run the script."""
    user_value = input("Enter the name of the desired product: ")
    urls = parse_connect(user_value)
    get_data(urls)
    cleaned_df = clear_data('result.csv')
    if cleaned_df is not None:
        feature_engineering(cleaned_df)
    logger.info('Script finished.')


if __name__ == '__main__':
    main()