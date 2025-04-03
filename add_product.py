import os
import validators

product_links = []

os.chdir("D:/Documents/Python/Amazkart")

BASE_LINK = "https://www.amazon.in/dp/"
with open("D:/Documents/Python/Amazkart/products.csv", "r") as pf:
    existing_links = pf.readlines()

product_ids = [
    pl.split(",")[2].split("/")[-1].replace("\n", "") for pl in existing_links
]
# print(product_ids)

while True:
    link = input("enter product link: \n")
    # link = "https://www.amazon.in/Creative-USB-Powered-Speakers-Far-Field-Radiators/dp/B0791H74NT/ref=sr_1_4?dib=eyJ2IjoiMSJ9.uY-gfq8TXRPwCKkURDzxRurkRLudc4BecbitTzTuF9SvE_t3MoGkGmzwa742ctoMyH5J1nJNe-1s-wyr9JlxI8JeN1PLMguyh9GhXufIgot4aKaMCpPBMPhhIr-DMwhnEfFPU5jrs592o563ivHHnT2ycnZdYaVdEGdIq7rEP8Bv1GDQfEG-h194FTzx5ro8NC0tsfBV-_ifq80gnxngeIw9R52Hy_AdSsMKLaU7g-c.Tg95DmvMlOqwgR0CXGFkW__q-iMHE2IZI_CsD913qUs&dib_tag=se&keywords=creative+speakers&qid=1722338216&sr=8-4"

    # # link = "https://www.amazon.in/gp/product/B0B25NXWC7/ref=ox_sc_act_title_1?smid=AJ6SIZC8YQDZX&psc=1"
    # link = "https://www.amazon.in/gp/product/B08ZJFH7Y1/ref=ox_sc_saved_image_1?smid=A14CZOWI0VEHLG&psc=1"

    if link == "" or validators.url(link) is False:
        break

    if validators.url(link):
        if "gp" in link:
            link_list = link.split("/")[:-1]
            product_id = link_list[-1]
            new_link = BASE_LINK + product_id
        else:
            link_list = link.split("/")
            del link_list[3]
            new_link = link_list[:5]
            product_id = new_link[-1]
            new_link = "/".join(new_link)
        if product_id in product_ids:
            print("Product already exists")
            continue
        print(new_link)
        product_line = f",0,{new_link}\n"
        product_links.append(product_line)

    file_path = f"data/{product_id}.csv"
    if not os.path.exists(file_path):
        with open(file_path, "w") as data_file:
            data_file.write("Date,Price\n")

if len(product_links) >= 1:
    for pl in product_links:
        existing_links.append(pl)

    with open("D:/Documents/Python/Amazkart/products.csv", "w") as pf:
        pf.writelines(existing_links)
