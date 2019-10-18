#!/usr/bin/env python3


from agora_analytica.loaders.yle_2019 import download_dataset

import click


@click.group()
def cli():
    pass

@cli.command()
@click.option("--target", type=click.Path())
def download(target=None):
    """
    Download dataset
    """

    data = download_dataset(target) if target else download_dataset()
    click.echo(f"Dataset downloaded")


if __name__ == "__main__":
    cli()
