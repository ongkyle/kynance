import argparser
from robinhood.robinhood import *
from env import *
from scraper import Downloader
import concurrent.futures

DEFAULT_REQUIRES_ENV_VAR = True
REQUIRED_ENV_VARS = {
    "--rh-username": "RH_USERNAME",
    "--rh-password": "RH_PASSWORD",
    "--rh-mfa": "RH_MFA",
    "--optionslam-username": "OPTIONSLAM_USERNAME",
    "--optionslam-password": "OPTIONSLAM_PASSWORD"}
PARSER_CONFIG = {
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
    "--ignore": {
        "metavar": "i",
        "type": str,
        "required": False,
        "action": "store",
        "nargs": "*",
        "help": "",
        "dest": "ignore"
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
        description="Download historical earnings data from all rh watchlists"
    )
    kwargs = {key: value for key, value in args.items()}
    arg_type = create_arg_type(**kwargs)
    return arg_type()


def watchlist_symbols(username, password, mfa_code, ignore):
    rh = Robinhood(username=username, password=password, mfa_code=mfa_code)
    watchlists_symbols = dict()
    unique = set()
    with rh:
        watchlists_symbols = rh.get_watchlists_symbols()
        watchlists_symbols = filter_watchlists(ignore, watchlists_symbols)
    for symbols in watchlists_symbols.values():
        if symbols is not None:
            unique.update(symbols)
    return list(unique)


def filter_watchlists(ignore, watchlists):
    return {k: v for k, v in watchlists.items() if k not in ignore}


def download(ticker, optionslam_username, optionslam_password, file):
    print(f"Downloading symbol: {ticker} to file: {file}")

    login_payload = {
        "username": optionslam_username,
        "password": optionslam_password,
        "next": "/"
    }

    headers = {
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Connection": "keep-alive",
        "Origin": "https://www.optionslam.com",
        "Host": "www.optionslam.com",
        "Method": "POST",
        "Referer": "https://www.optionslam.com/accounts/login/",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0"
    }

    with Downloader(needs_login=True, login_payload=login_payload,
                    base_url="https://www.optionslam.com",
                    download_postfix="/earnings/excel/" + ticker,
                    login_postfix="/accounts/os_login/",
                    csrf_attr="csrfmiddlewaretoken",
                    headers=headers) as d:
        d.download(file)
    return f"Finished Downloading symbol: {ticker} to file: {file}"


def submit_fn_to_executor(executor, fn, tickers, username, password):
    future_to_symbol = dict()
    for symbol in tickers:
        destination_dir = f"/home/kyle/workspace/kynance/data/{symbol}/"
        destination_file = os.path.join(destination_dir, "earnings.csv")
        future = executor.submit(
            fn,
            symbol,
            username,
            password,
            destination_file
        )
        future_to_symbol[future] = symbol
    return future_to_symbol


def resolve_futures(futures):
    for future in concurrent.futures.as_completed(futures):
        res = futures[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (res, exc))
        else:
            print(data)


def main():
    args = parse_args()
    rh_username = args.rh_username
    rh_password = args.rh_password
    rh_mfa = args.rh_mfa
    optionslam_username = args.optionslam_username
    optionslam_password = args.optionslam_password
    ignore = args.ignore

    symbols_to_fetch = watchlist_symbols(rh_username, rh_password, rh_mfa, ignore)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_symbol = submit_fn_to_executor(executor, download, symbols_to_fetch, optionslam_username,
                                                 optionslam_password)
        resolve_futures(future_to_symbol)


if __name__ == "__main__":
    main()
