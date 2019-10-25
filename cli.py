#!/usr/bin/env python3

import logging
import os.path

import webbrowser

import agora_analytica.loaders.yle_2019 as dataset
from agora_analytica.loaders.utils import _instance_path
from agora_analytica.analytics import measure_distances

import click

from flask.json import dumps as jsonify


@click.group()
@click.option("--debug/--no-debug", default=False, help="Show debug output")
def cli(debug):
    logging.basicConfig(level=(logging.DEBUG if debug else logging.INFO))


@cli.command()
@click.option("--target", type=click.Path())
def download(target=None):
    """
    Download dataset
    """

    data = dataset.download_dataset(target) if target else dataset.download_dataset()
    click.echo(f"Dataset downloaded")


@cli.command()
@click.option("--target", type=click.Path(file_okay=False), default=_instance_path(), show_default=True)
@click.option("--method", type=click.Choice(['linear', 'dummy']), help="Distance approximation method.", default="linear")
@click.option("--limit", default=50)
def build(target, limit, method):
    """
    Build page.

    :param target: Target file
    :param limit: Limit processing into N candidates.
    """

    def _write(file, data):
        """ Helper to write data into json file """

        with open(os.path.join(target, f"{file}.json"),'w') as f:
            print("\n", file, data)
            f.write(jsonify(data))
        

    click.echo("Loading dataset ... ", nl=False)
    df = dataset.load_dataset()
    if limit < 2:
        raise click.BadParameter("Build should include more than 2 candidates.", param_hint="--limit")
    df = df.head(limit)
    click.echo("[DONE]")

    click.echo("Calculating distances ... ", nl=False)
    answers = dataset.linear_answers(df)
    distances = measure_distances(answers, method=method)
    click.echo("[DONE]")

    click.echo("Writing data ... ", nl=False)

    data_nodes = [{
        "index": idx,
        "name": row["nimi"],
        "party": row["puolue"],
        "constituencies": row["vaalipiiri"]
    } for idx, row in df.iterrows()]

    data_links = [{
        "source": int(i),
        "distance": float(d),
        "target": int(l)
        } for i, d, l in distances.values]

    _write("nodes", data_nodes)

    _write("links", data_links)

    click.echo("[DONE]")





if __name__ == "__main__":
    cli()
