#!/usr/pin/python
import pandas as pd
import numpy as np
import array
import os.path
import json
from ..utils import instance_path

instancepath = instance_path() / "yle_scrape"
instancepath.mkdir(exist_ok=True)

IMAGE_BASE_URL = "https://ehdokaskone.yle.webscale.fi/"


def attach_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    attached scraped data to data frame
    """

    with open(os.path.join(instancepath, f"parties.json"), "r",encoding='utf-8') as json_file:
        parties = json.load(json_file)

    with open(os.path.join(instancepath, f"constituencies.json"), "r",encoding='utf-8') as json_file:
        constituencies = json.load(json_file)

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

                                # If candidate data is missing, skip.
                                if candidate['first_name'] is None and candidate['last_name'] is None:
                                    return df

                                if (candidate["info"]["election_promise_1"]["fi"] == promise):
                                    turha = 1
                                    df.at[i, 'name'] = "{first_name} {last_name}".format(**candidate)
                                    df.at[i, 'number'] = str(candidate["election_number"])
                                    df.at[i, 'image'] = f"{IMAGE_BASE_URL}{candidate['image']}"
        return df

    for i, row in df.iterrows():
        promise = row['Mitkä ovat kolme vaalilupaustasi? Vaalilupaus 1:']
        constituency = row['vaalipiiri']
        party = row['party']
        df = search_andsetvalues(promise, constituency, party, df, i)
    return df



if __name__ == "__main__":
    print("combine.py main does nothing currently by itself")