#!/usr/pin/python
from requests import get
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError
from contextlib import closing
#from bs4 import BeautifulSoup
import json
import os.path
from os import getcwd
from os import mkdir
from pathlib import Path
from .utils import _instance_path




def json_to_file (lista,name):

    f = open(os.path.join(instance_path(), f"{name}.json"),"w",encoding='utf-8')
    json.dump(lista,f, ensure_ascii=False)
    f.close()
    return


#jsonToFile(cont,"constituencies")

def hae_dataa():
    url = "https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/"
    r = get(url)
    #cont = json.loads(r.content)
    cont = r.json()

    dir = instance_path()
    if not os.path.exists(dir):
        os.mkdir(dir)

    json_to_file(cont,"constituencies")


    for constituent in cont:
        r = get("https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/" + str(constituent["id"]) + "/candidates")
        cont2 = r.json()
        json_to_file(cont2,"constituent" + str(constituent["id"]))

        for candidate in cont2:
            r = get("https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/" + str(constituent["id"]) + "/candidates/" + str(candidate["id"]))
            cont3 = r.json()
            json_to_file(cont3,"candidate" + str(candidate["id"]))

            try:
                pic= get("https://ehdokaskone.yle.webscale.fi/" + candidate["image"], timeout=10)

            except exceptions.ConnectionError:
                print ('exception')
        #continue
        
            candidate_id = candidate["id"]

            fp = open(os.path.join(instance_path(), f"{candidate_id}.jfif"),'wb')
            fp.write(pic.content)
            fp.close()


    url = "https://vaalikone.yle.fi/eduskuntavaali2019/api/public/parties"
    r = get(url)
    cont = r.json()
    #print(cont)
    json_to_file(cont,"parties")
    return

if __name__ == "__main__":

    text = input("Do you want to scrape data, THIS MIGHT TAKE UP TO 15 minutes Y/N? ") 
    if (text == "Y"):
        hae_dataa()



#Screippaus osotteet
#Vaalipiirin ID:n saa: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies
#Vaalipiirin ehokkaat: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/<vaalipiirin-id>/candidates
#Kandidaatin tiedot: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/<vaalipiirin-id>/candidates/<ehdokkaan-id>
#Kuva: https://ehdokaskone.yle.webscale.fi/kuvat/ekv2019/<ehdokas-id>/<kuvan-id>
#Puolueet: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/parties
