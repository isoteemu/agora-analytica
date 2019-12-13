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
#from .interpolation.combine import instancepath
from .utils import instance_path

path = os.path.join(instance_path(), "yle_scrape")
#path = instancepath
if not (os.path.exists(path)):
    mkdir(path)


def json_to_file(lista, name):
    """
    save json data to a json file with the given name
    """
    f = open(os.path.join(path, f"{name}.json"),"w",encoding='utf-8')
    json.dump(lista, f, ensure_ascii=False)
    f.close()
    return


def save_candidate(content, id, image_url):
    """
    save candidate's data to a json file
    """
    json_to_file(content, "candidate" + str(id))

    """
    if not isinstance(image_url, type(None)):
        try:
            pic= get("https://ehdokaskone.yle.webscale.fi/" + image_url, timeout=10)

        except ConnectionError:
            print('picture not found')

        fp = open(os.path.join(path, f"{id}.jpeg"),'wb')
        fp.write(pic.content)
        fp.close()
    """
    return


def hae_dataa():
    """
    scrape data from yle
    """

    url = "https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/"
    r = get(url)
    cont = r.json()
    json_to_file(cont, "constituencies")

    left = 2437
    found_candidates = []


    for constituent in cont:
        r = get("https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/" + str(constituent["id"]) + "/candidates")
        cont2 = r.json()
        json_to_file(cont2,"constituent" + str(constituent["id"]))

        for candidate in cont2:
            r = get("https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/" + str(constituent["id"]) + "/candidates/" + str(candidate["id"]))
            cont3 = r.json()
            save_candidate(cont3, candidate['id'], candidate['image'])
            found_candidates.append(candidate['id'])


    # cause there is 2437 candidates we assume that none of them has an id higher than 3000
    possible_not_foundcandidates = list(set(range(1, 3000)) - set(found_candidates))
    print(possible_not_foundcandidates)


    # getting leftover candidates that arent for some reason listed in their constituent's candidate list
    while len(possible_not_foundcandidates) > 0:
        for constituent in cont:
                r = get("https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/" + str(constituent["id"]) + "/candidates/" + str(possible_not_foundcandidates[0]))
                cont3 = r.json()
                if 'id' in cont3:
                    save_candidate(cont3, cont3['id'], cont3['image'])
                    break
        possible_not_foundcandidates.pop(0)
    

    url = "https://vaalikone.yle.fi/eduskuntavaali2019/api/public/parties"
    r = get(url)
    cont = r.json()
    json_to_file(cont, "parties")
    return


if __name__ == "__main__":

    text = input("Do you want to scrape data, THIS MIGHT TAKE UP TO 35 minutes Y/N? ") 
    if (text.upper() == "Y"):
        hae_dataa()


#Screippaus osotteet
#Vaalipiirin ID:n saa: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies
#Vaalipiirin ehokkaat: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/<vaalipiirin-id>/candidates
#Kandidaatin tiedot: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/<vaalipiirin-id>/candidates/<ehdokkaan-id>
#Kuva: https://ehdokaskone.yle.webscale.fi/kuvat/ekv2019/<ehdokas-id>/<kuvan-id>
#Puolueet: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/parties
