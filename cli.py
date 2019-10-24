#!/usr/bin/env python3

import logging
import os.path

import webbrowser

import agora_analytica.loaders.yle_2019 as dataset
from agora_analytica.loaders.utils import _instance_path
from agora_analytica.analytics import measure_distances

import click
from jinja2 import (
    Environment,
    PackageLoader,
    select_autoescape
)

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
@click.option("--target", type=click.Path(), default=_instance_path("build.html"))
@click.option("--limit", default=50)
def build(target, limit):
    """
    Build page.

    :param target: Target file
    :param limit: Limit processing into N candidates.
    """
    env = Environment(
        loader=PackageLoader('agora_analytica', 'templates')
    )

    click.echo("Loading dataset ... ", nl=False)
    df = dataset.load_dataset() 
    click.echo("[DONE]")

    click.echo("Calculating distances ... ", nl=False)
    answers = dataset.linear_answers(df)
    distances = measure_distances(answers, limit, method="linear")
    click.echo("[DONE]")

    click.echo("Generating page ... ", nl=False)

    data = [{
        "source": "%s (%s)" % (df.at[int(i),"nimi"], df.at[int(i),"puolue"]),
        "distance": d,
        "target": "%s (%s)" % (df.at[int(l),"nimi"], df.at[int(l),"puolue"])
        } for i, d, l in distances.values]
    #data = [{i, d, l] for i, d, l in distances.values]

    template = env.get_template("main.html")
    with open(target, "w") as f:
        f.write(template.render(data=data))
    click.echo("[DONE]")

    webbrowser.open(f"file:///{target}")


if __name__ == "__main__":
    cli()
