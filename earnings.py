import argparser
from cmds.download_all import DownloadAll
from cmds.journal import Journal, JournalBackfill, JournalUpdate
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
    "--optionslam-password": "OPTIONSLAM_PASSWORD",
    "--journal-file-path": "JOURNAL_FILE_PATH",
    "--data-dir": "DATA_DIR",
    "--data-source": "DEFAULT_CLIENT"
}

PARSER_CONFIG = {
    "--file": {
        "metavar": "file",
        "type": str,
        "required": False,
        "action": "store",
        "help": "csv file containing optionslam data for a single ticker",
        "dest": "file",

    },
    "--days": {
        "metavar": "days",
        "type": int,
        "required": False,
        "action": "store",
        "default": 30,
        "help": "number of days to calculate historical statistics",
        "dest": "days"
    },
    "--rh-username": {
        "metavar": "robinhood username",
        "type": str,
        "required": False,
        "action": "store",
        "default": DEFAULT_REQUIRES_ENV_VAR,
        "help": "robinhood username, usually your email. can also set RH_USERNAME env var",
        "dest": "rh_username"
    },
    "--rh-password": {
        "metavar": "robinhood password",
        "type": str,
        "required": False,
        "action": "store",
        "default": DEFAULT_REQUIRES_ENV_VAR,
        "help": "robinhood password. can also set RH_PASSWORD env var",
        "dest": "rh_password"
    },
    "--rh-mfa": {
        "metavar": "robinhood mfa code",
        "type": str,
        "required": False,
        "action": "store",
        "default": DEFAULT_REQUIRES_ENV_VAR,
        "help": "robinhood password. can also set RH_MFA env var",
        "dest": "rh_mfa"
    },
    "--tickers": {
        "metavar": "tickers",
        "type": str,
        "required": False,
        "action": "store",
        "nargs": "*",
        "default": DEFAULT_REQUIRES_ENV_VAR,
        "help": "ticker(s) / symbol(s) to fetch",
        "dest": "tickers"
    },
    "--optionslam-username": {
        "metavar": "optionslam username",
        "type": str,
        "required": False,
        "action": "store",
        "default": DEFAULT_REQUIRES_ENV_VAR,
        "help": "optionslam.com username",
        "dest": "optionslam_username"
    },
    "--optionslam-password": {
        "metavar": "optionslam password",
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
    },
    "--max-workers": {
        "metavar": "max workers",
        "required": False,
        "type": int,
        "default": None,
        "action": "store",
        "help": "number of workers generating a report",
        "dest": "max_workers"
    },
    "--journal": {
        "required": False,
        "action": "store_true",
        "help": "option to update trading journal with latest entries",
        "dest": "do_journal"
    },
    "--backfill-journal": {
        "required": False,
        "action": "store_true",
        "help": "option to backfill trading journal with all entries",
        "dest": "do_journal_backfill"
    },
    "--journal-file-path": {
        "metavar": "journal file path",
        "type": str,
        "required": False,
        "action": "store",
        "default": DEFAULT_REQUIRES_ENV_VAR,
        "help": "absolute file location of journal.csv",
        "dest": "journal_file_path"
    },
    "--ignore": {
        "default": [None],
        "metavar": "i",
        "type": str,
        "required": False,
        "action": "store",
        "nargs": "*",
        "help": "",
        "dest": "ignore"
    },
    "--download-all": {
        "required": False,
        "action": "store_true",
        "help": "option to download all historical earnings data",
        "dest": "do_download"
    },
    "--data-dir": {
        "metavar": "directory to store data",
        "type": str,
        "required": False,
        "action": "store",
        "default": DEFAULT_REQUIRES_ENV_VAR,
        "help": "absolute data dir",
        "dest": "data_dir"
    },
    "--data-source": {
        "metavar": "which datasource to use",
        "type": str,
        "required": False,
        "action": "store",
        "default": DEFAULT_REQUIRES_ENV_VAR,
        "help": "available datasources include: 'robinhood' or 'y_finance'",
        "dest": "client",
        "choices": ["robinhood", "y_finance"]
    }
}


def get_parser_config():
    config = {}
    ensure_env_vars(REQUIRED_ENV_VARS.values())
    for name, arg_config in PARSER_CONFIG.items():
        if arg_config.get("default", None) == DEFAULT_REQUIRES_ENV_VAR:
            arg_config["default"] = parse_env_var(REQUIRED_ENV_VARS[name])
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
    if args.do_journal:
        return JournalUpdate(
            args.journal_file_path,
            args.rh_username,
            args.rh_password,
            args.rh_mfa
        )
    elif args.do_journal_backfill:
        return JournalBackfill(
            args.journal_file_path,
            args.rh_username,
            args.rh_password,
            args.rh_mfa
        )
    elif not (args.do_report or args.do_journal or args.do_download):
        return TickerReport(args.tickers[0], args.days,
                            args.rh_username, args.rh_password,
                            args.rh_mfa, args.optionslam_username,
                            args.optionslam_password, args.client)
    elif args.do_report:
        return ManyTickerReport(
            args.max_workers,
            args.tickers,
            args.days,
            args.rh_username, args.rh_password,
            args.rh_mfa, args.optionslam_username,
            args.optionslam_password
        )
    elif args.do_download:
        return DownloadAll(
            args.data_dir,
            args.rh_username,
            args.rh_password,
            args.rh_mfa,
            args.optionslam_username,
            args.optionslam_password,
            args.ignore,
            args.client
        )


def main():
    args = parse_args()
    cmd = create_cmd(args)
    cmd.execute()


if __name__ == "__main__":
    main()
