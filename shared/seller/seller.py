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
