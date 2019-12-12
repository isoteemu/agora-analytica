#!/usr/pin/python
from requests import get
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError
from contextlib import closing
import json
import os.path
from os import getcwd
from os import mkdir
from pathlib import Path
from .interpolation.combine import instancepath



def json_to_file(lista, name):

    with open(instancepath / f"{name}.json", "x") as f:
        json.dump(lista, f, ensure_ascii=False)

    return


def hae_dataa():
    url = "https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/"
    r = get(url)
    cont = r.json()

    json_to_file(cont,"constituencies")


    for constituent in cont:
        r = get("https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/" + str(constituent["id"]) + "/candidates")
        cont2 = r.json()
        json_to_file(cont2,"constituent" + str(constituent["id"]))

        for candidate in cont2:
            r = get("https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/" + str(constituent["id"]) + "/candidates/" + str(candidate["id"]))
            cont3 = r.json()
            json_to_file(cont3,"candidate" + str(candidate["id"]))

    url = "https://vaalikone.yle.fi/eduskuntavaali2019/api/public/parties"
    r = get(url)
    cont = r.json()
    json_to_file(cont,"parties")
    return

if __name__ == "__main__":

    text = input("Do you want to scrape data, THIS MIGHT TAKE UP TO 15 minutes Y/N? ") 
    if (text.upper() == "Y"):
        hae_dataa()



#Screippaus osotteet
#Vaalipiirin ID:n saa: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies
#Vaalipiirin ehokkaat: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/<vaalipiirin-id>/candidates
#Kandidaatin tiedot: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/<vaalipiirin-id>/candidates/<ehdokkaan-id>
#Kuva: https://ehdokaskone.yle.webscale.fi/kuvat/ekv2019/<ehdokas-id>/<kuvan-id>
#Puolueet: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/parties
