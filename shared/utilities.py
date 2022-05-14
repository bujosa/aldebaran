import math

#Common fields
fields = { "year":"Año", "brand": "Marca", "model": "Modelo", "fuelType": "Tipo de combustible", "transmission": "Transmisión", "bodyStyle": "Tipo de carrocería",  "doors":"Puertas",  "engine": "Motor",  "mileage": "Kilómetros", "color": "Color", "dólares": "USD" , "pesos": "DOP"}

# Constants variables
limit_car_per_config = 1969
max_vehicle_per_page = 48

# This function is used to extract the uri
def convert_url(url):
    result = url.split("?")
    return result[0]

# This function is used to extract information from a tableBody
def data_sheet(soup):
    data = {}
    try: 
        columns = soup.find("tbody", class_="andes-table__body").find_all("tr")
    except: 
        return data

    for row in columns:
        key = row.find("th").text
        value = row.find("td").text
        data[key] = value
    
    return data

# This function is used to extract the date
def days_section(soup):
    title = soup.find("span", class_="ui-pdp-subtitle")

    if title == None:
        return None

    date = title.text.split("Publicado hace ")[1]
    keys = date.split(" ")

    if keys[1] == 'días' or keys[1] == 'día' :
          return int(keys[0])
    elif keys[1] == "año" or keys[1] == 'años' :
      return int(keys[0]) * 365
    else:  
      return int(keys[0]) * 30

# This function is used to get data from the data sheet
def key_error(data, key):
    try:
        if key == "year" or key == "mileage":
            return int(data[fields[key]].replace(" km",""))
        else:
            return data[fields[key]]
    except:
        return None
        
# This function is used to get the state of the car
def state_section(soup):
    try: 
        seller_info = soup.findAll("div", class_="ui-seller-info__status-info")
        for seller_info_status in seller_info:
            title = seller_info_status.find("h3", class_="ui-seller-info__status-info__title ui-vip-seller-profile__title").text
            if title == "Ubicación del vehículo":
                return seller_info_status.find("p", class_="ui-seller-info__status-info__subtitle").text.split(" - ")[1]
    except:
        return ''

def get_array_of_url(url, value):
    array_of_url = []
    last_part = "_Desde_"
    array_of_url.append(url)
    count = value/max_vehicle_per_page

    if count < 1 or value == max_vehicle_per_page: 
        return array_of_url
    else:
        count = math.floor(count)   
        for x in range(count+1):
            number = str(x*max_vehicle_per_page + 1)
            last_part_tmp = url+last_part+number
            array_of_url.append(last_part_tmp)
    
    return array_of_url

#Extract total pages
def get_config_url(soup):
    config_href = {}

    try: 
        config_div = soup.find(class_="ui-search-search-modal-grid-columns").find_all("a", class_="ui-search-search-modal-filter ui-search-link")
    except:
        return config_href

    for config in config_div:
        key = config.get("href")
        url = convert_url(key)
        config_href[url] = limit_car_per_config

    return config_href

def get_key(key):
    return fields[key]

def get_model(dict, title, brand):
  if title == None:
    return None

  model = title.replace(brand, "")

  for key in dict:
      if key == "Transmisión" or key == "Puertas":
          continue
      model = model.replace(dict[key], "")
  try:
      return model.split()[0]
  except: 
      return model 

def get_count():
    return limit_car_per_config