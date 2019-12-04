#!/usr/pin/python
import pandas as pd
import numpy as np
import array
import os.path
import json
from ..utils import instance_path
from ..scrape import hae_dataa


instancepath = instance_path()
try:
    instancepath = instance_path()
    with open(os.path.join(instancepath, f"parties2.json"), "r",encoding='utf-8') as json_file:
        parties = json.load(json_file)

    with open(os.path.join(instancepath, f"constituencies.json"), "r",encoding='utf-8') as json_file:
        constituencies = json.load(json_file)
except FileNotFoundError:
    text = input("Seems like you are missing some data. Do you want to scrape now, THIS MIGHT TAKE UP TO 15 minutes Y/N? ") 
    if (text == "Y"):
        hae_dataa()
    else:
        raise Exception("Missing data")


j = 1
constituentArray = []
constituentArray.append("")
while j <= 14:
    try:
        with open(os.path.join(instancepath, f'constituent' + str(j) + '.json'), "r",encoding='utf-8') as json_file:
            constituentArray.append(json.load(json_file))
    except FileNotFoundError:
        constituentArray.append("")
    j += 1


def attach_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    attached scraped data to data frame
    """
    for i, row in df.iterrows():
        promise = row['Mitkä ovat kolme vaalilupaustasi? Vaalilupaus 1:']
        constituency = row['vaalipiiri']
        party = row['party']
        df = search_andsetvalues(promise, constituency, party, df, i)
    return df


def search_andsetvalues(promise, constituency, party, df: pd.DataFrame, i) -> pd.DataFrame:

    candidate = "-"
    for const in constituencies:
        if (const["name_fi"] == constituency):
            for part in parties:
                if (part["name_fi"] == party):
                    for cand in constituentArray[const["id"]]:
                        if (cand["party_id"] == part["id"]):
                            with open(os.path.join(instancepath, f"candidate" + str(cand["id"]) + ".json"), "r",encoding='utf-8') as json_file:
                                    candidate = json.load(json_file)
                            if (candidate["info"]["election_promise_1"]["fi"] == promise):
                                turha = 1
                                df.at[i,'name',] =  candidate["first_name"] + " " + candidate["last_name"]
                                df.at[i, 'number'] = str(candidate["election_number"])
                                df.at[i,'yle_image'] = str(candidate["id"]) + ".jfif"  
    return df


if __name__ == "__main__":
    print("combine.py main does nothing currently by itself")