from bs4 import BeautifulSoup
import requests
from datetime import datetime
from datetime import timedelta
from database.mongo_dom import VehicleDataManagerDom
from shared.picture.picture import get_gallery_pictures
from shared.prices.price import price_section_dop
from shared.seller.seller import get_seller, get_seller_type
from shared.utilities import data_sheet, days_section, get_array_of_url, get_config_url, get_model, key_error, state_section
from concurrent.futures import ThreadPoolExecutor

# Request to mercado mercado libre RD
response = requests.get('https://carros.mercadolibre.com.do/autos-camionetas/_FiltersAvailableSidebar?filter=VEHICLE_YEAR')
mercadoLibre = response.text
soup = BeautifulSoup(mercadoLibre, "html.parser")

global_count = 0
days_limit = 7
total_vehicles = 0

# Create ThreadPoolExecutor
workers = ThreadPoolExecutor(max_workers=80)

# Get car information
def get_car_information(url):
    response = requests.get(url)
    vehicle_detail_page = response.text
    soup = BeautifulSoup(vehicle_detail_page, "html.parser")

    picture_section = soup.find("img", class_="ui-pdp-image ui-pdp-gallery__figure__image")
    if picture_section == None:
        return
    
    pictures, len_pictures = get_gallery_pictures(soup)
    if len_pictures < 4 or len(pictures) < 4:
        return

    replace_text = "Imagen 1 de " + str(len_pictures) + " de "
    
    title = picture_section.get("alt").replace(replace_text, "").replace("  ", " ")
    if title == None:
        return
    
    brand = title.split(" ")[0]

    price, currency = price_section_dop(soup)
    if price == None:
        return

    days = days_section(soup)
    if days > days_limit:
        return

    sellerType = get_seller_type(soup)
    if sellerType != 'Particular':
        return

    data_sheet_table = data_sheet(soup)

    # vehicle brand and model validation
    model = get_model(data_sheet_table, title, brand)
    if key_error(data_sheet_table, "brand") != None:
        brand = key_error(data_sheet_table, "brand")
    if key_error(data_sheet_table, "model") != None:
        model = key_error(data_sheet_table, "model")
    if brand == None or model == None:
        return
    # end of vehicle brand and model validation

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

    # Insert vehicle in database
    VehicleDataManagerDom().addCar(vehicle)
    

# Extract vehicle url 
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
            global global_count
            global_count += 1

            print("Veces que me itero: " + str(global_count))

            car_url = url.find("a", class_="ui-search-result__content ui-search-link").get("href")
            workers.submit(get_car_information, car_url)

# Main Function
def maindom(days):
    global days_limit
    days_limit = days
    global total_vehicles

    config_url_and_count, total_vehicles = get_config_url(soup)

    for key in config_url_and_count:
        get_car_url(key, config_url_and_count[key])
    
    print("Yo me ejecuto al final del todo")