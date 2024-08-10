from selenium import webdriver
import time
from bs4 import BeautifulSoup
import pandas as pd
from config import headers, service, options


def get_content(url):
    try:
        driver = webdriver.Firefox(service=service, options=options)
        driver.get(url)
        time.sleep(5)

        page_sourse = driver.page_source
        print("HTML content successfully loaded")
        return page_sourse

    except Exception as err:
        print("Something went wrong", err)
    finally:
        driver.quit()


def get_item_urls(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    item_divs = soup.findAll('div', class_='product-card__wrapper')

    urls = []
    for i, div in enumerate(item_divs):
        if i >= 50:
            break
        link = div.find("a", class_='product-card__link j-card-link j-open-full-product-card')
        if link:
            item_url = link.get('href')
            if item_url.startswith('/'):
                item_url = f"https://www.wildberries.ru{item_url}"
            urls.append(item_url)

    print("Urls collected successfully")
    return urls


def get_data(urls_list):
    driver = webdriver.Firefox(service=service, options=options)
    result_list = []

    for url in urls_list:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        try:
            item_name = soup.find('h1', class_="product-page__title")
            if item_name:
                item_name = item_name.get_text(strip=True)
                print(f"Item name is - {item_name}")
            else:
                print(f"No product name found for URL: {url}")

            item_company_name = soup.find('a',
                                          class_='product-page__header-brand j-wba-card-item j-wba-card-item-show j-wba-card-item-observe')
            if item_company_name:
                item_company_name = item_company_name.get_text(strip=True)
                print(f"The name of the company that released the product is  - {item_company_name}")
            else:
                print(f"This product has no manufacturer")

            item_product_rating = soup.find('span',
                                            class_="product-review__rating address-rate-mini address-rate-mini--sm")
            if item_product_rating:
                item_product_rating = item_product_rating.get_text(strip=True)
                print(f"Product rating is - {item_product_rating}")
            else:
                print(f"No one has left a review for the product yet")

            item_count_reviews = soup.find('span',
                                           class_='product-review__count-review j-wba-card-item-show j-wba-card-item-observe')
            if item_count_reviews:
                item_count_reviews = item_count_reviews.get_text(strip=True)
                item_count_reviews_t = ''.join(filter(str.isdigit, item_count_reviews))
                print(f"Product already has - {item_count_reviews_t} reviews")
            else:
                print(f"No one has left a review for the product yet")

            item_price = soup.find('ins', class_="price-block__final-price wallet")
            if item_price:
                item_price = item_price.get_text(strip=True)
                print(f"The current price of the product is - {item_price}")
            else:
                print(f"That product doesn't have price")

            images_urls = []
            item_image = soup.find('div', class_='zoom-image-container').find('img',
                                                                              class_='photo-zoom__preview j-zoom-image hide')
            if item_image:
                item_image = item_image.get('src')
                images_urls.append(item_image)
                print(item_image)

            result_list.append(
                {
                    'item_url': url,
                    'item_name': item_name,
                    'item_company_name': item_company_name,
                    'item_product_rating': item_product_rating,
                    'item_count_reviews': item_count_reviews_t,
                    'item_price': item_price,
                    'item_image': item_image
                }
            )

        except Exception as err:
            print(f"Error processing {url}: {err}")

    driver.quit()

    # to csv
    df = pd.DataFrame(result_list)
    df.to_csv("result.csv", index=False, encoding='utf-8')
    print("Data successfully saved to 'result.csv'")


def parse_connect(user_value: str):
    url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={user_value}"
    html_content = get_content(url)
    urls = get_item_urls(html_content)
    return urls


def main():
    user_value = input("Enter the name of the desired product: ")
    urls = parse_connect(user_value)
    get_data(urls)


if __name__ == '__main__':
    main()
