from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import time
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
}


service = Service('D:/FoxDriver/geckodriver.exe')
options = webdriver.FirefoxOptions()
options.add_argument('--headless')


def get_content(url):
    try:
        driver = webdriver.Firefox(service=service, options=options)
        driver.get(url)
        time.sleep(5)

        with open("Wild.html", 'w', encoding='utf-8') as file:
            file.write(driver.page_source)
        print("HTML was successfully loaded into 'Wild.html'")

    except Exception as err:
        print("Something went wrong", err)
    finally:
        driver.quit()


def get_item_urls(file_path):
    try:
        with open(file_path, 'rb') as file:
            src = file.read().decode('utf-8', errors='ignore')
    except UnicodeDecodeError as e:
        print(f"Ошибка декодирования: {e}")
        return []

    soup = BeautifulSoup(src, 'lxml')
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

    with open("Wild.html", 'w', encoding='utf-8') as file:
        for url in urls:
            file.write(f"{url}\n")

    print("Urls collected successfully")
    return urls


def get_data(fileURL_path):
    with open(fileURL_path) as file:
        urls_list = [url.strip() for url in file.readlines()]

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
            item_image = soup.find('div', class_ = 'zoom-image-container').find('img', class_ = 'photo-zoom__preview j-zoom-image hide')
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
    df.to_csv("result.csv", index=False, encoding='utf-8-sig')
    print("Data successfully saved to 'result.csv'")
    print("Data successfully saved to 'result.csv'")


def parse_connect(user_value: str):
    url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={user_value}"
    get_content(url)


def main():
    user_value = input("Enter the name of the desired product: ")
    parse_connect(user_value)
    get_item_urls("D:/PythonProjects/Wildb/Wild.html")
    get_data("D:/PythonProjects/Wildb/Wild.html")


if __name__ == '__main__':
    main()
