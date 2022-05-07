# This function is used to get pictures from the gallery and get the number of pictures
def get_gallery_pictures(soup):
    pictures = []
    try:
        gallery_pictures = soup.find("div", class_="ui-pdp-gallery__column").find_all("span", class_="ui-pdp-gallery__wrapper")
        for picture in gallery_pictures:
            pictures.append(picture.find("img", class_="ui-pdp-image").get("src").replace("R.jpg", "F.jpg").replace("O.jpg", "F.jpg"))
        if len(pictures) > 5:
            return pictures[0:4], len(pictures)
        return pictures, len(pictures)
    except:
        return [], len(pictures)
