# This function is used to get the price of the car and the currency
from shared.utilities import get_key

def price_section_dop(soup):
    price_section = soup.find("span", class_="andes-visually-hidden")

    if price_section == None:
        return None
    
    keys = price_section.text.split(" ")
    
    price = int(keys[0])
    tmp = get_key(keys[1])

    currency = "DOP"
    
    if tmp == "dólares":
        currency = "USD"

    
    if price > 200 and price < 999:
        return price*1000, "DOP"

    if price < 2000: 
        return None, None

    if price < 100000 and currency == "DOP": 
        currency =  "USD"

    return price, currency

def price_section_mex(soup):
    price_section = soup.find("span", class_="price-tag-fraction")

    if price_section == None:
        return None

    price = int(price_section.text.replace(",",""))
    return price

def price_section_cop(soup):
    price_section = soup.find("span", class_="price-tag-fraction")

    if price_section == None:
        return None

    price  = price_section.text.replace(",","")
    price = price.replace(".","")
    return int(price)
