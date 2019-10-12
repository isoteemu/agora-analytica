#!/usr/bin/env python3

"""
Testejä etäisyyksien laskennasta.
"""

from panda_io import (
    lue_data_sisään, VAALIDATA_TIEDOSTO,
)

import pandas as pd
import numpy as np
import click


@click.command()
@click.argument("tiedosto", type=click.Path(exists=True), default=VAALIDATA_TIEDOSTO)
@click.option("--määrä", default=10)
@click.option("--menetelmä", type=click.Choice(['etäisyys_poikkeavuudella', 'etäisyys_mean']), default="etäisyys_poikkeavuudella")
def etäisyyksiä(tiedosto, määrä: int, menetelmä):
    """
    Vertailee etäisyyksiä satunnaiselle joukolle ehdokkaita.
    """

    # Luetaan vaalidata
    vaalidata = lue_data_sisään(tiedosto)

    # Valitse satunnaiset ehdokkaat, ja skaalakysymykset.
    vertailtavat = vaalidata.sample(määrä + 1).fillna(3)
    vastaukset = vaalidata.iloc[:, 4:33].fillna(3).astype('int')

    # Valitse yksi ehdokkaista, ja poista se vertailtavista.
    lähde = vertailtavat.sample(1)
    vertailtavat.drop(index=lähde.iloc[0, 0], inplace=True)

    print(lähde["puolue"].iloc[0], "/", lähde["vaalipiiri"].iloc[0])

    etäisyydet = []

    for kohde_idx, kohde in vertailtavat.iterrows():
        # Obs, vaarallista koodausta alla.
        etäisyys = globals()[menetelmä](lähde, kohde, vastaukset)
        etäisyydet.append((etäisyys, " ".join([kohde["puolue"], "/", kohde["vaalipiiri"]])))

    for etäisyys, ehdokas in sorted(etäisyydet, key=lambda x: x[0]):
        print("\t", ehdokas, etäisyys)


def etäisyys_mean(lähde, kohde, vastaukset):
    """
    Laskee etäisyyden vertailemalla vastausten etäisyyksien keskiarvoa.
    """

    # `diff()` laskee rivin eron edelliseen -> tulos jotain väliltä (1-5) – (5-1)
    # `tail(1)` ottaa n riviä lopusta - eli viimeisen
    # `applymap(np.abs)` muuttaa kaikki arvot positiivisiksi luvuiksi.

    erot = lähde.append(kohde)[vastaukset.columns].astype("int").diff().tail(1).applymap(np.abs)
    return np.float(erot.mean(axis=1))


def etäisyys_poikkeavuudella(lähde: pd.DataFrame, kohde: pd.DataFrame, vastaukset: pd.DataFrame) -> np.float:

    # Asteikko jota kysymykset käyttävät.
    ASTEIKON_SKAALA = 5

    keskiarvot = pd.Series()

    for sarake in vastaukset:
        # Käy vastaukset läpi yksitellen.

        # Osoitin sarakkeeseen - kysymykseen - jota käsitellään
        col = vastaukset[sarake]

        # Kerää ehdokkaiden vastaukset. `set()` pitää huolta ettei sama vastaus toistu useampaan kertaan.
        vertailtavien_vastaukset = set([
            np.int(lähde[sarake]),
            np.int(kohde[sarake])
        ])

        # Laske keskiarvo kuinka monta on vastannut samoin, ja kuinka monta erillailla.
        # `isin()` luo listan True/False arvoilla, ja saadulla listalla suodatetaan vain True arvot. laskentaan.
        # Tilde taas vaihtaa arvot toisinpäin.
        samoin_vastanneita = col[col.isin(vertailtavien_vastaukset)].count() / len(vertailtavien_vastaukset)
        muutoin_vastanneita = col[~col.isin(vertailtavien_vastaukset)].count() / (ASTEIKON_SKAALA - len(vertailtavien_vastaukset))

        # Varmista arvo järkevälle skaalalle.
        painotin = min(2.0, max(0.1, muutoin_vastanneita / samoin_vastanneita))

        # Laske etäisyys, ja varmista se olevan positiivinen luku alkeisluvulla.
        etäisyys = abs(np.int(lähde[sarake]) - np.int(kohde[sarake])) * painotin

        keskiarvot = keskiarvot.append(pd.Series([etäisyys]), ignore_index=True)

    etäisyys_mean = np.float(keskiarvot.mean())
    return etäisyys_mean


if __name__ == "__main__":
    etäisyyksiä()
