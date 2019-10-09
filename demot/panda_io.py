"""
Esimerkki miten ladataan data, ja luetaan se pandas -kirjaston DataFrame luokaksi.

"""

# tarvitaan `pandas` kirjasto
import pandas as pd
# Käytetään `requests` kirjastoa noutamaan data.
import requests
# `BytesIO` tarjoaa liiman, jolla voidaan virtuaalisena tiedostona antaa
# bittijono luettavaksi functiolle, joka odottaa tiedostokuvaajaa.
from io import BytesIO
# Vaalidata on zip tiedosto, se pitää purkaa jotenkin.
from zipfile import ZipFile

# Komentorivikomentoja varten käytetään click kirjastoa.
import click


VAALIDATA_AINEISTO = "https://vaalit.beta.yle.fi/avoindata/avoin_data_eduskuntavaalit_2019.zip"
VAALIDATA_TIEDOSTO = "Avoin_data_eduskuntavaalit_2019_valintatiedot.csv"


def lataa_ylen_data(url=VAALIDATA_AINEISTO, tiedosto=VAALIDATA_TIEDOSTO) -> pd.DataFrame:
    """
    Lukee datan ylen sivuilta.
    """

    # Ladataan vaalidata ylen sivuilta. `VAALIDATA_AINEISTO`
    # on määritelty ylempänä
    r = requests.get(url)

    # Jos lataus epäonnistuu, epäonnistu nyt.
    # `raise_for_status()` tarkastaa onko webpalvelin palauttanut
    # tiedoston vai ei, ja onko se ladattu onnistuneesti.
    # Nimensä mukaan aiheuttaa keskeytyksen - raise - jos virhe havaittiin.
    r.raise_for_status()

    if r.headers['content-type'] != "application/zip":
        raise ConnectionError("Ladattu tiedosto ei ollut zip")

    with ZipFile(BytesIO(r.content)) as pakattu_tiedosto:
        # Avataan saatu data Bitteinä, tällöin meidän ei tarvitse tallettaa
        # zip tiedostoa tiedostojärjestelmään odottamaan.

        # Puretaan haluttu tiedosto, ja kääritään pandan dataframen ympärille.
        data = pd.read_csv(BytesIO(pakattu_tiedosto.read(tiedosto)))

    return data


def lue_data_sisään(tiedosto) -> pd.DataFrame:
    """ Lukee datan sisään """
    data = pd.read_csv(tiedosto)
    return data


@click.group()
def cli():
    """
    Tämä on ohje joka näkyy komentorivillä.

    ..example:
        $ python3 panda_io.py puolueet

    Jos näissä käytetyt decoraattorit - `@click` ja `@cli` ei heti aukea, ei kannata harmistua.
    Decoraattorit ympäröivät alla olevan funktion:
    https://en.wikipedia.org/wiki/Python_syntax_and_semantics#Decorators
    """

    # pass on pythonin null operaattori, eli ei tee mitään. Tämän funktion
    # tarkoituksena onkin vain kertoa `click`ille, että meillä on tällainen
    # komentoryhmä kuin `cli`.
    pass


@cli.command("lataa")
@click.argument('kohde', type=click.Path(), default=VAALIDATA_TIEDOSTO)
def tallenna_tiedosto(kohde):
    """
    Tallentaa Ylen vaalidatan johonkin.

    ..example:
        $ python3 panda_io.py lataa [kohde-tiedosto.csv]

    :param kohde: Tiedostonnimi johon tiedosto tallennetaan.
    """

    data = lataa_ylen_data()
    data.to_csv(kohde)
    click.echo(f"Tiedosto tallennettu: {kohde!r}")


@cli.command("puolueet")
@click.argument('tiedosto', type=click.Path(exists=True), default=VAALIDATA_TIEDOSTO)
def listaa_puolueet(tiedosto):
    """
    Listaa puolueet.
    """

    data = lue_data_sisään(tiedosto)
    click.echo("Datasetin uniikkeja puolueita ovat:")

    # Hienosti ilmaistu for loop. Se luo listan olemassa olevasta listasta,
    # mutta sitä ei tallenneta muuttujaan. Se sijaan jokainen alkio käsitellään
    # jollain funktiolla - `click.echo()` - joka tulostaa alkion komentoriville.
    # Vertaa print(), mutta kontekstiherkkä.
    [click.echo(f" * {puolue}") for puolue in data.puolue.unique()]


if __name__ == '__main__':
    cli()
