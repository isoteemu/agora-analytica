"""

YLE EDUSKUNTAVAALIT 2019
~~~~~~~~~~~~~~~~~~~~~~~~

Functions for processing data from Yle Eduskuntavaalit 2019.

"""

import logging
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

import re

from .utils import _instance_path, generate_names

log = logging.getLogger(__name__)

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
        log.debug("File downloaded as:", filepath)

    return data


def load_dataset(tiedosto=DATASET_PATH) -> pd.DataFrame:
    """ Read dataset """
    df = pd.read_csv(tiedosto)
    df = process_data(df)
    return df


def process_data(df: pd.DataFrame):
    """
    Run processing functions for data.
    """

    df.columns = df.columns.map(clean_column)
    df = convert_linear_into_int(df)

    return df


def clean_column(x):
    """ Clean string. """
    # Remove line endings.
    x = x.replace("\n", "")
    # Strip extra spaces and commas
    x = re.sub(r"\.(\s*\.+)", r".", x)
    return clean_string(x)


def clean_string(x):
    if isinstance(x, (np.str, str)):
        x = re.sub(r'(\s)\s+', r'\1', x)
        x = x.strip()

    return x


def convert_linear_into_int(df: pd.DataFrame) -> pd.DataFrame:
    """ Converts linear values into :type:`np.int` """
    linear_ranges = [
        ("Suomen pitää olla edelläkävijä ilmastonmuutoksen vastaisessa taistelussa, vaikka se aiheuttaisi suomalaisille kustannuksia.", "On oikein nähdä vaivaa sen eteen, ettei vahingossakaan loukkaa toista."),
        ("Uusimaa. Kaatolupia on myönnettävä nykyistä enemmän susikannan rajoittamiseksi.", "Uusimaa. Metro tulee jatkaa Helsingistä Sipooseen.", ("vaalipiiri", "Uudenmaan vaalipiiri")),
        ("Helsinki. Kun Helsinki sulkee hiilivoimaloita, voidaan korvaavaa energiaa tuottaa ydinvoimalla.", "Helsinki. Metro tulee jatkaa Helsingistä Sipooseen.", ("vaalipiiri", "Helsingin vaalipiiri")),
        ("Varsinais-Suomi. Kaatolupia on myönnettävä nykyistä enemmän susi-, merimetso- ja hyljekantojen rajoittamiseksi.", "Varsinais-Suomi. Saariston yhteysalusliikenteen jatkuvuuden turvaamiseksi liikenteen tulisi olla maksullista kesäasukkaille ja matkailijoille.", ("vaalipiiri", "Varsinais-Suomen vaalipiiri")),
        ("Satakunta. Satakuntaan tulisi rakentaa runsaasti lisää tuulivoimaloita.", "Satakunta. Porin lentokentän henkilöliikenteen tukeminen olisi rahan haaskausta.", ("vaalipiiri", "Satakunnan vaalipiiri")),
        ("Ahvenanmaa. Ahvenanmaan erivapauksia on rajoitettava.", "Ahvenanmaa. Ahvenanmaan demilitarisointi tulisi ottaa uudelleen pohdintaan Itämerellä kasvaneen sotilaallisen aktiivisuuden vuoksi.", ("vaalipiiri", "Ahvenanmaan maakunnan vaalipiiri")),
        ("Häme. Hämeeseen ei saa avata yhtään uutta kaivosta ennen kuin yhtiöiltä aletaan periä kaivosveroa.", "Häme. Tietulleja voidaan kerätä Hämeen teiden kunnossapidon parantamiseksi.", ("vaalipiiri", "Hämeen vaalipiiri")),
        ("Pirkanmaa. Tampereen ei pidä enää antaa täyttää järvien rantoja rakentamista varten.", "Pirkanmaa. Helsinki-Tampere-junayhteyttä on parannettava niin, että juna kulkee kaupunkien välin vain tunnissa.", ("vaalipiiri", "Pirkanmaan vaalipiiri")),
        ("Kaakkois-Suomi. Saimaan luontoarvoista voidaan tinkiä, jotta kaivosteollisuuteen syntyisi uusia työpaikkoja.", "Kaakkois-Suomi. Parikkalan rajanylityspaikka tulee avata kansainväliselle liikenteelle.", ("vaalipiiri", "Kaakkois-Suomen vaalipiiri")),
        ("Savo-Karjala. Jos koululaisen koulumatkan pituus on yli tunnin suuntaansa, on yhtenä päivänä viikossa oltava mahdollisuus etäkoulunkäyntiin.", "Savo-Karjala. Raitiotieliikenne on realistinen tapa parantaa julkista liikennettä Itä-Suomessa.", ("vaalipiiri", "Savo-Karjalan vaalipiiri")),
        ("Vaasa. Kaatolupia on myönnettävä nykyistä enemmän susi-, merimetso- ja hyljekantojen rajoittamiseksi.", "Vaasa. Maahanmuuttoa pitää lisätä, jotta maakuntien reunakunnissakin riittäisi asukkaita ja työvoimaa.", ("vaalipiiri", "Vaasan vaalipiiri")),
        ("Keski-Suomi. Jyväskylän kaupunginteatterin ja museoiden kunnostamiseen on seuraavalla hallituskaudella ohjattava merkittäviä valtionavustuksia.", "Keski-Suomi. Jyväskylän on saatava nykyistä enemmän valtiontukea joukkoliikenteensä järjestämiseen.", ("vaalipiiri", "Keski-Suomen vaalipiiri")),
        ("Oulun vaalipiiri. Valtion pitää vähentää selvästi omistusosuuttaan Sotkamon Talvivaarassa kaivostoimintaa harjoittavasta Terrafame-yhtiöstä.", "Oulun vaalipiiri. Oulusta on tällä vuosikymmenellä tullut entistä turvattomampi paikka elää.", ("vaalipiiri", "Oulun vaalipiiri")),
        ("Lappi. Lappiin ei saa avata yhtään uutta kaivosta ennen kuin yhtiöiltä aletaan periä kaivosveroa.", "Lappi. Jäämeren rata pitää rakentaa.", ("vaalipiiri", "Lapin vaalipiiri")),
    ]
    for cols in linear_ranges:
        if len(cols) == 3:
            f, t, i = cols

            matrix = df.loc[df[i[0]] == i[1], f:t]
            df.loc[df[i[0]] == i[1], f:t] = matrix.fillna(np.int(3)).astype('int')
        else:
            f, t = cols
            matrix = df.loc[:, f:t].fillna(np.int(3)).astype('int')
            df.loc[:, f:t] = matrix
    return df


if __name__ == "__main__":
    print(f"Loading dataset from: {DATASET_PATH}")
    dataset = load_dataset()
    size = dataset.shape[0]
    print(f"Number of entries: {size}")
