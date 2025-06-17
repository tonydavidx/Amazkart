from itertools import product
import os
import re
import validators

product_csv_file = "D:/Documents/Python/Amazkart/data/products.csv"

product_links = []

os.chdir("D:/Documents/Python/Amazkart")

BASE_LINK = "https://www.amazon.in/dp/"
with open(product_csv_file, "r") as pf:
    existing_links = pf.readlines()
# print(product_ids)


while True:
    link = input("enter product link: \n")
    # link = "https://www.amazon.in/OnePlus-Wireless-Earbuds-Drivers-Playback/dp/B0C8JB3G5W?crid=2539ZAH1CCIQ0&dib=eyJ2IjoiMSJ9.2yTjrwJE21k8wlrL_GhTibJ3zpuH_UVTXx-T0-lJibeluADa-HMIccpsuf1DF4ZyVyNVqKlvUNrJAh3kSYHVaUq19Ps_8am0vEwc70lI3QmKryghz9e0M7N7UEvHcg-nWMpBmlt8RN69ZmpytwrELnaDG2KjrrGVia1vnR7nM-ZOtbnOJwW8Uf1lhabAlafTegXmau81Kh9azN9e6069Vk0CRtv9vs8gW5I7LkdRzoE.RYCL0_5_YCrmjCQ4Yid2cgEkHHzyvDXdLjkd807p5gc&dib_tag=se&keywords=tws&nsdOptOutParam=true&qid=1749476969&sprefix=tws%2Caps%2C290&sr=8-3&th=1"

    # # link = "https://www.amazon.in/gp/product/B0B25NXWC7/ref=ox_sc_act_title_1?smid=AJ6SIZC8YQDZX&psc=1"
    # link = "https://www.amazon.in/gp/product/B08ZJFH7Y1/ref=ox_sc_saved_image_1?smid=A14CZOWI0VEHLG&psc=1"

    if link == "" or validators.url(link) is False:
        break

    if validators.url(link):
        pattern = r"/dp/([A-Z0-9]{10})"
        match = re.search(pattern, link)

        if match:
            product_id = match.group(1)
            print(product_id)  # Output: B0C8JB3G5W
        else:
            print("Product ID not found.")

        product_links.append(f",0,{BASE_LINK}{product_id}\n")

    print(len(product_links), "products added")

    if len(product_links) >= 1:
        for pl in product_links:
            existing_links.append(pl)

        with open(product_csv_file, "w") as pf:
            pf.writelines(existing_links)
