# IMPORTATIONS
import datetime
import json
import logging

from modules.ghostfolio import get_bearer_token, import_activity

from degiro_connector.trading.api import API as TradingAPI
from degiro_connector.trading.models.trading_pb2 import (
    Credentials,
    TransactionsHistory,
)

# SETUP LOGGING LEVEL
logging.basicConfig(level=logging.DEBUG)

# SETUP CONFIG DICT
with open("config/config.json") as config_file:
    config_dict = json.load(config_file)

# SETUP CREDENTIALS
int_account = config_dict.get("degiro_int_account")
username = config_dict.get("degiro_username")
password = config_dict.get("degiro_password")
ghostfolio_auth_token = config_dict.get("ghostfolio_auth_token")
ghostfolio_api_host = config_dict.get("ghostfolio_api_host")

gf_bearer_token = get_bearer_token(ghostfolio_api_host, ghostfolio_auth_token)
import_activity(gf_bearer_token, accountId="", currency="", dataSource="", date="", fee="", quantity="", symbol="", type="", unitPrice="")

exit(1)

credentials = Credentials(
    username,
    password,
    int_account,
    # totp_secret_key=totp_secret_key,
    # one_time_password=one_time_password,
)

# SETUP TRADING API
trading_api = TradingAPI(credentials=credentials)

# CONNECT
trading_api.connect()

# SETUP REQUEST
today = datetime.date.today()
from_date = TransactionsHistory.Request.Date(
    year=today.year,
    month=1,
    day=1,
)
to_date = TransactionsHistory.Request.Date(
    year=today.year,
    month=today.month,
    day=today.day,
)
request = TransactionsHistory.Request(
    from_date=from_date,
    to_date=to_date,
)

# FETCH DATA
transactions_history = trading_api.get_transactions_history(
    request=request,
    raw=False,
)

# DISPLAY TRANSACTIONS
for transaction in transactions_history.values:
    print(dict(transaction))