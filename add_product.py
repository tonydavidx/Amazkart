import validators
product_links = []

while True:
    link = input('enter product link: \n')
    # link = "https://www.amazon.in/Creative-USB-Powered-Speakers-Far-Field-Radiators/dp/B0791H74NT/ref=sr_1_4?dib=eyJ2IjoiMSJ9.uY-gfq8TXRPwCKkURDzxRurkRLudc4BecbitTzTuF9SvE_t3MoGkGmzwa742ctoMyH5J1nJNe-1s-wyr9JlxI8JeN1PLMguyh9GhXufIgot4aKaMCpPBMPhhIr-DMwhnEfFPU5jrs592o563ivHHnT2ycnZdYaVdEGdIq7rEP8Bv1GDQfEG-h194FTzx5ro8NC0tsfBV-_ifq80gnxngeIw9R52Hy_AdSsMKLaU7g-c.Tg95DmvMlOqwgR0CXGFkW__q-iMHE2IZI_CsD913qUs&dib_tag=se&keywords=creative+speakers&qid=1722338216&sr=8-4"

    if link == '':
        break

    if validators.url(link):
        link_list = link.split('/')
        del (link_list[3])
        new_link = link_list[:5]
        new_link = "/".join(new_link)
        print(new_link)
        product_line = f",0,{new_link}\n"
        product_links.append(product_line)


if len(product_links) >= 1:

    with open('D:/Documents/Python/Amazkart/products.csv', 'r') as pf:
        existing_links = pf.readlines()

    for pl in product_links:
        existing_links.append(pl)

    with open('D:/Documents/Python/Amazkart/products.csv', 'w') as pf:
        pf.writelines(existing_links)
