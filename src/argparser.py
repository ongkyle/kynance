import argparse


def create_parser(config, description):
    parser = argparse.ArgumentParser(description=description)
    for name, config in config.items():
        parser.add_argument(
            name,
            **config,
        )
    return parser


def parse_args(config, description):
    parser = create_parser(config, description)
    return vars(parser.parse_args())
