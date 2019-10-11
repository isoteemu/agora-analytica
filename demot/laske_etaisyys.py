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

    # Otetaan kaksi ehdokasta sample() metodilla, ja heidän vastaukset.
    # Muutetaan samalla tekstidata numeraaliseksi (`int`).
    for i in range(määrä):
        # vertailtavat = vaalidata.head(2)
        vertailtavat = vaalidata.sample(2)
        vastaukset = vertailtavat.iloc[:, 4:33].dropna(axis=1).astype('int')

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


if __name__ == "__main__":
    etäisyys()
