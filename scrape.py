#!/usr/pin/python
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json
import os.path
from os import getcwd
from os import mkdir
from pathlib import Path


url = "https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/"
r = get(url)
cont = json.loads(r.content)




dir = os.path.join(Path.cwd(),'instance')
if not os.path.exists(dir):
    os.mkdir(dir)


def jsonToFile (lista,name):

    f = open(os.path.join(Path.cwd() / 'instance', f"{name}.json"),"w",encoding='utf-8')
    json.dump(lista,f, ensure_ascii=False)
    f.close()
    return


jsonToFile(cont,"constituencies")



for constituent in cont:
    r = get("https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/" + str(constituent["id"]) + "/candidates")
    cont2 = json.loads(r.content)
    jsonToFile(cont2,"constituent" + str(constituent["id"]))

    for candidate in cont2:
        r = get("https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/" + str(constituent["id"]) + "/candidates/" + str(candidate["id"]))
        cont3 = json.loads(r.content)
        jsonToFile(cont3,"candidate" + str(candidate["id"]))

        try:
            pic= get("https://ehdokaskone.yle.webscale.fi/" + candidate["image"], timeout=10)

        except exceptions.ConnectionError:
            print ('exception')
        #continue
        
        candidateID = candidate["id"]

        fp = open(os.path.join(Path.cwd() / 'instance', f"{candidateID}.jfif"),'wb')
        fp.write(pic.content)
        fp.close()



url = "https://vaalikone.yle.fi/eduskuntavaali2019/api/public/parties"
r = get(url)

cont = json.loads(r.content)
print(cont)

jsonToFile(cont,"parties")


#Vaalipiirin ID:n saa: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies
#Vaalipiirin ehokkaat: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/<vaalipiirin-id>/candidates
#Kandidaatin tiedot: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/constituencies/<vaalipiirin-id>/candidates/<ehdokkaan-id>
#Kuva: https://ehdokaskone.yle.webscale.fi/kuvat/ekv2019/<ehdokas-id>/<kuvan-id>
#Puolueet: https://vaalikone.yle.fi/eduskuntavaali2019/api/public/parties
