import argparser
from cmds.many_ticker_report import ManyTickerReport
from cmds.ticker_report import TickerReport
from env import *

DEFAULT_REQUIRES_ENV_VAR = True


REQUIRED_ENV_VARS = {
    "--rh-username": "RH_USERNAME",
    "--rh-password": "RH_PASSWORD",
    "--rh-mfa": "RH_MFA",
    "--tickers": "TICKERS",
    "--optionslam-username": "OPTIONSLAM_USERNAME",
    "--optionslam-password": "OPTIONSLAM_PASSWORD"}

PARSER_CONFIG = {
    "--file": {
        "metavar": "f",
        "type": str,
        "required": False,
        "action": "store",
        "help": "csv file containing optionsslam data for a single ticker",
        "dest": "file",

    },
    "--days": {
        "metavar": "d",
        "type": int,
        "required": False,
        "action": "store",
        "default": 30,
        "help": "number of days to calculate historical statistics",
        "dest": "days"
    },
    "--rh-username": {
        "metavar": "rhu",
        "type": str,
        "required": False,
        "action": "store",
        "default": DEFAULT_REQUIRES_ENV_VAR,
        "help": "robinhood username, usually your email. can also set RH_USERNAME env var",
        "dest": "rh_username"
    },
    "--rh-password": {
        "metavar": "rhu",
        "type": str,
        "required": False,
        "action": "store",
        "default": DEFAULT_REQUIRES_ENV_VAR,
        "help": "robinhood password. can also set RH_PASSWORD env var",
        "dest": "rh_password"
    },
    "--rh-mfa": {
        "metavar": "rhmfa",
        "type": str,
        "required": False,
        "action": "store",
        "default": DEFAULT_REQUIRES_ENV_VAR,
        "help": "robinhood password. can also set RH_MFA env var",
        "dest": "rh_mfa"
    },
    "--tickers": {
        "metavar": "t",
        "type": str,
        "required": False,
        "action": "store",
        "nargs": "*",
        "default": DEFAULT_REQUIRES_ENV_VAR,
        "help": "ticker(s) / symbol(s) to fetch",
        "dest": "tickers"
    },
    "--optionslam-username": {
        "metavar": "osu",
        "type": str,
        "required": False,
        "action": "store",
        "default": DEFAULT_REQUIRES_ENV_VAR,
        "help": "optionslam.com username",
        "dest": "optionslam_username"
    },
    "--optionslam-password": {
        "metavar": "osp",
        "type": str,
        "required": False,
        "action": "store",
        "default": DEFAULT_REQUIRES_ENV_VAR,
        "help": "optionslam.com password",
        "dest": "optionslam_password"
    },
    "--report": {
        "required": False,
        "action": "store_true",
        "help": "option to generate a report for earnings within the next 7 days",
        "dest": "do_report"
    }
}

def get_parser_config():
    config = {}
    ensure_env_vars(REQUIRED_ENV_VARS.values())
    for name, arg_config in PARSER_CONFIG.items():
        if arg_config.get("default", None) == DEFAULT_REQUIRES_ENV_VAR:
            arg_config["default"] = os.getenv(REQUIRED_ENV_VARS[name])
        config[name] = arg_config
    return config


def create_arg_type(**kwargs):
    arg_type = type('Args', (object,), dict(**kwargs))
    return arg_type


def parse_args():
    config = get_parser_config()
    args = argparser.parse_args(
        config=config,
        description="Calculate historical data for options"
    )
    kwargs = {key: value for key, value in args.items()}
    arg_type = create_arg_type(**kwargs)
    return arg_type()


def create_cmd(args):
    if args.do_report == False:
        return TickerReport(args.tickers, args.days,
                            args.rh_username, args.rh_password,
                            args.rh_mfa, args.optionslam_username,
                            args.optionslam_password)
    elif args.do_report == True:
        return ManyTickerReport(
            args.tickers,
            args.days,
            args.rh_username, args.rh_password,
            args.rh_mfa, args.optionslam_username,
            args.optionslam_password
        )


def main():
    args = parse_args()
    cmd = create_cmd(args)
    cmd.execute()


if __name__ == "__main__":
    main()
