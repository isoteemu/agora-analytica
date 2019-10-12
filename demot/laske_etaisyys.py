#!/usr/bin/env python3

"""
Esimerkki etäisyyksien laskennasta.

Ottaa tiedostosta kaksi satunnaista ehdokasta, ja laskee heille etäisyyden.

"""

from panda_io import (
    lue_data_sisään, VAALIDATA_TIEDOSTO,
)

import pandas as pd
import numpy as np
import click


@click.command()
@click.argument("tiedosto", type=click.Path(exists=True), default=VAALIDATA_TIEDOSTO)
@click.option("--määrä", default=1)
def etäisyys(tiedosto, määrä: int):
    """
    Laskee kahden satunnaisen ehdokkaan etäisyyden.
    """

    # Luetaan vaalidata
    vaalidata = lue_data_sisään(tiedosto)

    for i in range(määrä):
        # Otetaan kaksi ehdokasta sample() metodilla, ja heidän vastaukset.
        # Muutetaan samalla tekstidata numeraaliseksi (`int`).
        # vertailtavat = vaalidata.head(2)
        vertailtavat = vaalidata.sample(2)
        vastaukset = vertailtavat.iloc[:, 4:33].fillna(3).astype('int')

        # Laske ero omalla funktiolla.
        ero_mean = laske_ero_mean(vastaukset)

        click.echo("{eka} ({eka_vp}) - {toka} ({toka_vp})\tMean: {ero}".format(
            eka=vertailtavat.iloc[0]["puolue"], eka_vp=vertailtavat.iloc[0]["vaalipiiri"],
            toka=vertailtavat.iloc[1]["puolue"], toka_vp=vertailtavat.iloc[1]["vaalipiiri"],
            ero=float(ero_mean)
            ))


def laske_ero_mean(vastaukset: pd.DataFrame):
    """
    Vertailee datasetin kahta viimeistä ehdokasta, ja laskee niiden etäisyyden.
    """

    # `diff()` laskee rivin eron edelliseen -> tulos jotain väliltä (1-5) – (5-1)
    # `tail(1)` ottaa n riviä lopusta - eli viimeisen
    # `applymap(np.abs)` muuttaa kaikki arvot positiivisiksi luvuiksi.
    erot = vastaukset.diff().tail(1).applymap(np.abs)
    return erot.mean(axis=1)


@click.command()
@click.argument("tiedosto", type=click.Path(exists=True), default=VAALIDATA_TIEDOSTO)
def etäisyys_poikkeavuudella(tiedosto):
    """
    Laskee kahden satunnaisen ehdokkaan etäisyyden ottaen huomioon vastausten poikkeavuuden massasta.
    """

    # Asteikko jota kysymykset käyttävät.
    ASTEIKON_SKAALA = 5

    # Luetaan vaalidata
    vaalidata = lue_data_sisään(tiedosto)

    # Valitse satunnaiset ehdokkaat, ja skaalakysymykset.
    vertailtavat = vaalidata.sample(2).fillna(3)
    vastaukset = vaalidata.iloc[:, 4:33].fillna(3).astype('int')

    print(vertailtavat.iloc[0]["puolue"], vertailtavat.iloc[0]["vaalipiiri"])
    print(vertailtavat.iloc[1]["puolue"], vertailtavat.iloc[1]["vaalipiiri"])

    keskiarvot = pd.Series()

    for sarake in vastaukset:
        # Käy vastaukset läpi yksitellen.

        col = vastaukset[sarake]

        # Kerää ehdokkaiden vastaukset. `set()` pitää huolta ettei sama vastaus toistu useampaan kertaan.
        vertailtavien_vastaukset = set([
            np.int(vertailtavat.iloc[0][sarake]),
            np.int(vertailtavat.iloc[1][sarake])
        ])

        # Laske keskiarvo kuinka monta on vastannut samoin, ja kuinka monta erillailla.
        # `isin()` luo listan True/False arvoilla, ja saadulla listalla suodatetaan vain True arvot. laskentaan.
        # Tilde taas vaihtaa arvot toisinpäin.
        samoin_vastanneita = col[col.isin(vertailtavien_vastaukset)].count() / len(vertailtavien_vastaukset)
        muutoin_vastanneita = col[~col.isin(vertailtavien_vastaukset)].count() / (ASTEIKON_SKAALA - len(vertailtavien_vastaukset))

        # Varmista arvo järkevälle skaalalle.
        painotin = min(2.0, max(0.1, muutoin_vastanneita / samoin_vastanneita))

        # Laske etäisyys kuten :func:`laske_ero_mean`. Pieni ero koska kyseessä on `Series` eikä `Dataframe`.
        etäisyys = abs(vertailtavat[sarake].astype('int').diff().iat[1]) * painotin

        # Tulostele debuggausta varten tietoa
        print(sarake, vertailtavien_vastaukset)
        print("\tSamoin:", samoin_vastanneita, "Muutoin:", muutoin_vastanneita, "Painotin", painotin)
        print("\tEtäisyys", etäisyys)

        keskiarvot = keskiarvot.append(pd.Series([etäisyys]), ignore_index=True)

    etäisyys_mean = keskiarvot.mean()
    print("Etäisyys mean", etäisyys_mean)
    return etäisyys_mean


if __name__ == "__main__":
    etäisyys_poikkeavuudella()
