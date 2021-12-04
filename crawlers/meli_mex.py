from bs4 import BeautifulSoup
import requests
from datetime import datetime
from datetime import timedelta
from database.mongo_mex import VehicleDataManagerMex
from shared.picture.picture import get_gallery_pictures
from shared.seller.seller import get_seller, get_seller_type
from shared.utilities import data_sheet, days_section, get_array_of_url, get_config_url, get_model, key_error, price_section_mex, state_section
import threading

# Request to mercado mercado libre mx
response = requests.get("https://autos.mercadolibre.com.mx/distrito-federal/trato-directo/_FiltersAvailableSidebar?filter=BRAND")
mercadoLibre = response.text
soup = BeautifulSoup(mercadoLibre, "html.parser")

count = 0
count_url = 0
days_limit = 7

# Get car information
def get_car_information(url):
    response = requests.get(url)
    vehicle_detail_page = response.text
    soup = BeautifulSoup(vehicle_detail_page, "html.parser")

    # picture_section validation
    picture_section = soup.find("img", class_="ui-pdp-image ui-pdp-gallery__figure__image")
    if picture_section == None:
        return
    # end picture_section validation

    # pictures validation section
    pictures, len_pictures = get_gallery_pictures(soup)
    if len_pictures < 4 or len(pictures) < 4:
        return
    # end pictures validation section

    # price_section validation
    price = price_section_mex(soup)
    if price == None:
        return
    # end price_section validation

    # days_section validation
    days = days_section(soup)
    if days > days_limit:
      return
    # end days_section validation

    data_sheet_table = data_sheet(soup)
    
    # brand and model validation
    replace_text = "Imagen 1 de " + str(len_pictures) + " de "
    title = picture_section.get("alt").replace(replace_text, "").replace("  ", " ")
    brand = title.split(" ")[0]
    model = get_model(data_sheet_table, title, brand)

    if key_error(data_sheet_table, "brand") != None:
            brand = key_error(data_sheet_table, "brand")
     
    if key_error(data_sheet_table, "model") != None:
        model = key_error(data_sheet_table, "model")
    
    if brand == None or model == None:
        return
    # end brand and model validation

    vehicle = {
       "title":title, 
       "brand": brand,
       "model":model,
       "price": price*0.95, 
       "originalPrice": price,
       "currency": 'MXN',
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
       "country": "Mexico",
       "state": state_section(soup),
       "seller": get_seller(soup),
       "sellerType": get_seller_type(soup),
       "createdAt": datetime.now().isoformat(),
       "postCreatedAt":  (datetime.now() - timedelta(days=days)).isoformat(),
    }

    global count
    count += 1
    print(count)
    print(url)

    thread_sun_sun = threading.Thread(target=VehicleDataManagerMex().addCar, args=[vehicle], daemon=True)
    thread_sun_sun.start()
    thread_sun_sun.join()

# Get car url
def get_car_url(key, value):
    brand_specific_urls = get_array_of_url(key, value)

    for specific_page in brand_specific_urls:
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
            global count_url
            count_url += 1
            print("Veces que me itero: " + str(count_url))
            car_url = url.find("a", class_="ui-search-result__content ui-search-link").get("href")
            thread_son = threading.Thread(target=get_car_information, args=[car_url], daemon=True)
            thread_son.start()
            thread_son.join()
            
# Main Function
def mainmex(days):
    global days_limit
    days_limit = days

    config_url_and_count = get_config_url(soup)

    for key in config_url_and_count:
        get_car_url(key, config_url_and_count[key])
    