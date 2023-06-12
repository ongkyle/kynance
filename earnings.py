import argparser
import logging.config
import yaml

from cmds.download_all import DownloadAll
from cmds.journal import JournalBackfill, JournalUpdate
from cmds.many_ticker_report import ManyTickerReport
from cmds.ticker_report import TickerReport
from env import *
from config import *


def init_logger():
    with open(LOG_CONFIG_FILE ,"r") as cfg_file:
        logging_cfg = yaml.safe_load(cfg_file)
        logging.config.dictConfig(logging_cfg)
    return logging.getLogger(__name__)
    

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
    return create_arg_type(**kwargs)


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
    logger = init_logger()
    logger.info("Initialized logger")
    args = parse_args()
    logger.info(f"Parsed args: {vars(args)}")
    cmd = create_cmd(args)
    logger.info(f"Executing cmd: {vars(cmd)}")
    cmd.execute()


if __name__ == "__main__":
    main()
