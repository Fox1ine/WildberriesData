import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
from my_config import SELENIUM_EXPLICIT_WAIT, headers, service, options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Initialize the logger
logger = logging.getLogger(__name__)


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
                if item_name:
                    logger.info(f"Item name is - {item_name}")
                else:
                    logger.warning(f"No product name found for URL: {url}")

                item_company_name = extract_item_data(soup, 'a', 'product-page__header-brand j-wba-card-item j-wba-card-item-show j-wba-card-item-observe')
                if item_company_name:
                    logger.info(f"The name of the company that released the product is - {item_company_name}")
                else:
                    logger.warning(f"This product has no manufacturer")

                item_product_rating = extract_item_data(soup, 'span', "product-review__rating address-rate-mini address-rate-mini--sm")
                if item_product_rating:
                    logger.info(f"Product rating is - {item_product_rating}")
                else:
                    logger.warning(f"No one has left a review for the product yet")

                item_count_reviews = extract_item_data(soup, 'span', 'product-review__count-review j-wba-card-item-show j-wba-card-item-observe')
                if item_count_reviews:
                    item_count_reviews_t = ''.join(filter(str.isdigit, item_count_reviews))
                    logger.info(f"Product already has - {item_count_reviews_t} reviews")
                else:
                    logger.warning(f"No one has left a review for the product yet")

                item_price = extract_item_data(soup, 'ins', "price-block__final-price wallet")
                if item_price:
                    logger.info(f"The current price of the product is - {item_price}")
                else:
                    logger.warning(f"This product doesn't have a price")

                images_urls = extract_item_data(soup, 'img', 'photo-zoom__preview j-zoom-image hide', multiple=True, get_attr='src')
                if images_urls:
                    logger.info(f"Image links are - {images_urls}")
                else:
                    logger.warning("Images not found")

                result_list.append(
                    {
                        'item_url': url,
                        'item_name': item_name,
                        'item_company_name': item_company_name,
                        'item_product_rating': item_product_rating,
                        'item_count_reviews': item_count_reviews_t,
                        'item_price': item_price,
                        'item_image': images_urls[0] if images_urls else None
                    }
                )

            except Exception as err:
                logger.error(f"Error processing {url}: {err}")

        # Save to CSV
        df = pd.DataFrame(result_list)
        df.to_csv("result.csv", index=False, encoding='utf-8', quoting=1) 
        logger.info("Data successfully saved to 'result.csv'")


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


if __name__ == '__main__':
    main()
