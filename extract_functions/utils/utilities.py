#Common fields
fields = { "year":"Año", "brand": "Marca", "model": "Modelo", "fuelType": "Tipo de combustible", "transmission": "Transmisión", "bodyStyle": "Tipo de carrocería",  "doors":"Puertas",  "engine": "Motor",  "mileage": "Kilómetros", "color": "Color", "dólares": "USD" , "pesos": "DOP"}

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
        
# This function is used to get the price of the car and the currency
def price_section(soup):
    price_section = soup.find("span", class_="price-tag-text-sr-only")

    if price_section == None:
        return None
    
    keys = price_section.text.split(" ")
    
    price = int(keys[0])
    currency = get_key(keys[1])
    
    if price > 200 and price < 999:
        return price*1000, "DOP"

    if price < 2000: 
        return None, None

    if price < 100000 and currency == "DOP": 
        currency =  "USD"

    return price, currency

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

# This function is used to get pictures from the gallery and get the number of pictures
def get_gallery_pictures(soup):
    pictures = []
    try:
        gallery_pictures = soup.find("div", class_="ui-pdp-gallery__column").find_all("span", class_="ui-pdp-gallery__wrapper")
        for picture in gallery_pictures:
            pictures.append(picture.find("img", class_="ui-pdp-image").get("data-src").replace("R.jpg", "F.jpg").replace("O.jpg", "F.jpg"))
        
        if len(pictures) > 5:
            return pictures[0:4], len(pictures)
        return pictures, len(pictures)
    except:
        return [], len(pictures)

def get_key(key):
    return fields[key]

def get_seller(soup):
    try:
        seller = soup.find("h3", class_="ui-pdp-color--BLACK ui-pdp-size--LARGE ui-pdp-family--REGULAR").text
        return seller
    except:
        return ''

def get_seller_type(soup):
    try:
        sellerType = soup.find("p", class_="ui-pdp-color--GRAY ui-pdp-family--REGULAR ui-vip-profile-info__subtitle").text
        return sellerType
    except:
        return 'Particular'

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