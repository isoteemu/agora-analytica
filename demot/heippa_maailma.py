#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Esimerkki pythonista
~~~~~~~~~~~~~~~~~~~~

Ensimmäinen rivi tässä tiedostossa kertoo käyttöjärjestelmälle tämän olevan python tiedosto.

Toinen rivi kertoo merkistön olevan utf-8, mutta tätä ei tarvita enää. Historiallisista syistä
sitä saatetaan nähdä varsinkin joissain yliopiston hommissa.

"""

# Import lause. Kuin javassa kutsuttaisiin luokkia, mutta kutsutaankin moduuleita.
from random import sample


def heippa_maailma() -> str:
    """
    Dokumentointi tulee funktion sisään, erityiseen docstring lohkoon.

    Tässä voisi sitten olla tarkempi kuvaus mitä funktion tekee, mutta ylin rivi on ns. summary.

    Yleisesti pythonin pep-8 määrittelee miten funktiot ja muuttujat tulee nimetä. Pienellä. Ei käyttäen CamelCasea.

    Funktion nimen jälkeen on type hint. Sitä ei tarvita, mutta se voi olla kehitysympäristön autocompleten kannalta
    hyödyllinen. Toinen keino määritellä return type on funktion kuvauksessa kertoa se.

    :rtype: str
    """

    # Koodin seassa käytetään risuaitaa kommenteissa. Python tulkki jättää nämä huomiotta,
    # mutta edellä oleva lohko kolmella tuumamerkillä taas on itse asiassa merkkijono, jota ei ole
    # suoraan määritelty millekkään muuttujalle. Dokumentointityökalut etsivät sitä, ja autocomplete
    # ottaa vihjeensä siitä.

    # Asetataan muuttuja. Tyyppiä ei tarvitse eksplisiittisesti sanoa.
    kuka = "maailma"

    # Joskus voi nähdä myös `kuka = u"maailma"`, joka määrittelee tyypin nimenomaan utf-8 merkkijonoksi.
    # Taas asia jota nykypäivänä ei tarvita. Mutta vastaavia prefiksejä on muitakin.

    # Merkkijonot voi yhdistää plussalla:
    lause_klassinen = "Heippa " + kuka + "!"

    # ... Mutta yleisempää on käyttää merkkijonojen formatointia. Joskus voi nähdä vielä:
    lause_vanha = "Heippa %s!" % kuka

    # mutta nykyään käytetään merkkijono-olion `format()` metodia:
    lause_uusi = "Heippa {}!".format(kuka)

    # tai sen uudempi shorthand
    lause_laiska = f"Heippa {kuka}!"

    # Muodostetaan yllä olevista lauseista lista, ja random moduulin `sample()` metodilla valitaan yksi.
    lause_sample = sample([lause_klassinen, lause_vanha, lause_uusi, lause_laiska], 1)

    # Yllä saatu `lause_sample` on lista, otetaan ensimmäinen listasta:
    lause = lause_sample[0]

    return lause


if __name__ == "__main__":
    # Vain jos ajetaan pää-ohjelmana, suorita tämän lohkon sisältö. Näin voidaan tätä
    # tiedostoa käyttää myös toisen ohjelman moduulina.
    print(heippa_maailma())
