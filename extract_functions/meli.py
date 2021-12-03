#Packages
from bs4 import BeautifulSoup
import requests
import math
from datetime import datetime
from datetime import timedelta
import os
import threading

# Extract function from the extract_functions root
from extract_functions.database.mongo import VehicleDataManager
from extract_functions.utils.utilities import convert_url, data_sheet, days_section, get_gallery_pictures, get_model, get_seller, get_seller_type, key_error, price_section, state_section

# Request to mercado mercado libre RD
response = requests.get(os.environ['MELI_ORIGIN'])
mercadoLibre = response.text
soup = BeautifulSoup(mercadoLibre, "html.parser")

# Constants variables
max_vehicle_per_page = 48
limit_car_per_year = 1969

count = 0

days_limit = 7

def get_array_of_url(url, value):
    year_url = []
    last_part = "_Desde_"
    year_url.append(url)
    count = value/max_vehicle_per_page

    if count < 1 or value == max_vehicle_per_page: 
        return year_url
    else:
        count = math.floor(count)
        for x in range(count+1):
            number = str(x*max_vehicle_per_page + 1)
            last_part_tmp = url+last_part+number
            year_url.append(last_part_tmp)
    
    return year_url

def get_car_information(url):
    response = requests.get(url)
    vehicle_detail_page = response.text
    soup = BeautifulSoup(vehicle_detail_page, "html.parser")

    picture_section = soup.find("img", class_="ui-pdp-image ui-pdp-gallery__figure__image")

    if picture_section == None:
        return
    
    pictures, len_pictures = get_gallery_pictures(soup)

    if len_pictures < 4:
        return

    replace_text = "Imagen 1 de " + str(len_pictures) + " de "
    
    title = picture_section.get("alt").replace(replace_text, "").replace("  ", " ")

    if title == None:
        return
    
    brand = title.split(" ")[0]

    price, currency = price_section(soup)

    if price == None:
        return

    days = days_section(soup)
    
    if days > days_limit:
        return

    sellerType = get_seller_type(soup)

    if sellerType != 'Particular':
        return

    data_sheet_table = data_sheet(soup)

    model = get_model(data_sheet_table, title, brand)

    if key_error(data_sheet_table, "brand") != None:
        brand = key_error(data_sheet_table, "brand")
     
    if key_error(data_sheet_table, "model") != None:
        model = key_error(data_sheet_table, "model")

    # vehicle brand and model validation
    if brand == None or model == None:
        return

    vehicle = {
       "title":title, 
       "brand": brand,
       "model": model,
       "price": price*0.95, 
       "originalPrice": price,
       "currency": currency,
       "mainPicture": pictures[0],
       "pictures": pictures[1:],
       "year": key_error(data_sheet_table, "year"),
       "fuelType": key_error(data_sheet_table, "fuelType"),
       "bodyStyle": key_error(data_sheet_table, "bodyStyle"),
       "transmission": key_error(data_sheet_table, "transmission"),
       "engine": key_error(data_sheet_table, "engine"),
       "doors": key_error(data_sheet_table, "doors"),
       "mileage": key_error(data_sheet_table, "mileage"),
       "color": key_error(data_sheet_table, "color"),
       "vehicle_url": url,
       "country": "Republica Dominicana",
       "state": state_section(soup),
       "seller": get_seller(soup),
       "sellerType": sellerType,
       "createdAt": datetime.now().isoformat(),
       "postCreatedAt":  (datetime.now() - timedelta(days=days)).isoformat(),
    }

    global count
    count += 1
    print(count)
    print(url)

    # VehicleDataManager().addCar(vehicle)
    thread_sun_sun = threading.Thread(target=VehicleDataManager().addCar, args=[vehicle], daemon=True)
    thread_sun_sun.start()
    thread_sun_sun.join()

def get_car_url(key, value):
    year_specific_urls = get_array_of_url(key, value)

    for specific_page in year_specific_urls:
        response = requests.get(specific_page)
        car_page = response.text
        soup = BeautifulSoup(car_page, "html.parser")

        validator = soup.find("svg", class_="ui-search-icon ui-search-icon--not-found ui-search-rescue__icon")
        
        if validator != None:
            break

        urls = soup.find("section", class_="ui-search-results")

        if urls == None:
            break
        else:
            urls = urls.find_all("li", class_="ui-search-layout__item")

        for url in urls:
            car_url = url.find("a", class_="ui-search-result__content ui-search-link").get("href")
            threading.Thread(target=get_car_information, args=[car_url], daemon=True).start()

def get_year_url(soup):
    year_href = {}

    try: 
        year_div = soup.find(class_="ui-search-search-modal-grid-columns").find_all("a", class_="ui-search-search-modal-filter ui-search-link")
    except:
        return year_href

    for year in year_div:
        key = year.get("href")
        
        value_tmp = year.find("span", class_="ui-search-search-modal-filter-match-count").text
        
        value = int(value_tmp.replace("(","").replace(")","").replace(",",""))

        url = convert_url(key)

        if value > limit_car_per_year:
            value = limit_car_per_year

        year_href[url] = value

    return year_href

# Main Function
def main(days):
    global days_limit
    days_limit = days

    year_url_and_count = get_year_url(soup)

    for key in year_url_and_count:
        get_car_url(key, year_url_and_count[key])
    