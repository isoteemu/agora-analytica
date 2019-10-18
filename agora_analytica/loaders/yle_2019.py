"""

YLE EDUSKUNTAVAALIT 2019
~~~~~~~~~~~~~~~~~~~~~~~~

Functions for processing data from Yle Eduskuntavaalit 2019.

"""

# `BytesIO` tarjoaa liiman, jolla voidaan virtuaalisena tiedostona antaa
# bittijono luettavaksi functiolle, joka odottaa tiedostokuvaajaa.
from io import BytesIO
# Vaalidata on zip tiedosto, se pitää purkaa jotenkin.
from zipfile import ZipFile

import numpy as np
# tarvitaan `pandas` kirjasto
import pandas as pd
# Käytetään `requests` kirjastoa noutamaan data.
import requests

from .utils import generate_names, _instance_path
import logging


DATASET_URL = "https://vaalit.beta.yle.fi/avoindata/avoin_data_eduskuntavaalit_2019.zip"
DATASET_NAME = "Avoin_data_eduskuntavaalit_2019_valintatiedot.csv"

# Dataset default path
DATASET_PATH = _instance_path(DATASET_NAME)

# column to use for dataframe index.
INDEX = "key"

def download_dataset(filepath=DATASET_PATH, url=DATASET_URL, **kwargs) -> pd.DataFrame:
    """
    Download dataset

    :param: file  Output filename
    """

    kwargs.setdefault("session", requests.Session())

    r = kwargs['session'].get(url)

    # Jos lataus epäonnistuu, epäonnistu nyt.
    # `raise_for_status()` tarkastaa onko webpalvelin palauttanut
    # tiedoston vai ei, ja onko se ladattu onnistuneesti.
    # Nimensä mukaan aiheuttaa keskeytyksen - raise - jos virhe havaittiin.
    r.raise_for_status()

    if r.headers['content-type'] != "application/zip":
        raise ConnectionError(f"Expected zip file, received {r.headers['content-type']}")

    with ZipFile(BytesIO(r.content)) as pakattu_tiedosto:
        # Avataan saatu data Bitteinä, tällöin meidän ei tarvitse tallettaa
        # zip tiedostoa tiedostojärjestelmään odottamaan.

        # Puretaan haluttu tiedosto, ja kääritään pandan dataframen ympärille.
        data = pd.read_csv(BytesIO(pakattu_tiedosto.read(DATASET_NAME)))

        # Replace with np.NaN, as Yle is using "-" to indicate skipped and no opinion
        # values
        data = data.replace("-", np.NaN)

        # Add names, if data has none.
        if "nimi" not in data.columns:
            nimet = pd.Series(generate_names(data.shape[0]), name="nimi")
            data = data.assign(nimi=nimet)

        data.to_csv(filepath, index_label=INDEX)
        logging.debug("File downloaded as:", filepath)

    return data


def read_dataset(tiedosto) -> pd.DataFrame:
    """ Read dataset """
    data = pd.read_csv(tiedosto)

    return 
