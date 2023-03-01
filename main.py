import datetime
import logging

from art import *
from asciistuff import Lolcat

import yfinance as yf

from config import AppConfig
from modules.ghostfolio import import_activity
from degiro_connector.trading.api import API as TradingAPI
from degiro_connector.trading.models.trading_pb2 import (
    Credentials,
    ProductsInfo,
    TransactionsHistory,
)

logging.basicConfig(level=logging.INFO)


# Say hi! 👋
message = text2art("DEGIRO >> GHOSTFOLIO")
print("")
print(Lolcat(message))
print("")


# Read configuration
config_dict = AppConfig().get()
int_account = config_dict.get("degiro_int_account")
username = config_dict.get("degiro_username")
password = config_dict.get("degiro_password")

credentials = Credentials(
    int_account = int(int_account),
    username = username,
    password = password
)

degiro_trading_api = TradingAPI(credentials=credentials)

try:
    degiro_trading_api.connect()
except:
    print(f"💩 Shit, cannot login to degiro")
    exit(1)


# Setup date period
today = datetime.date.today()
from_date = TransactionsHistory.Request.Date(
    year=2020,
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


# Fetch degiro transactions
transactions_history = degiro_trading_api.get_transactions_history(
    request=request,
    raw=False,
)

for transaction in transactions_history.values:
    trans = dict(transaction)
    logging.debug("[DEGIRO] [TRANSACTION]", trans)

    if trans['buysell'] != "S" and trans["buysell"] != "B":
        logging.error(f"Unknown transaction type: {trans['buysell']}")
        continue

    prodId = int(trans['productId'])
    dated = trans['date'].split("T")
    defdate = f"{dated[0]} {dated[1].split('+')[0]}"

    product_request = ProductsInfo.Request()
    product_request.products.extend([prodId])

    products_info = degiro_trading_api.get_products_info(
        request=product_request,
        raw=True
    )

    logging.debug("[DEGIRO] [PRODUCT]", products_info)

    transtype = "SELL" if trans['buysell'] == "S" \
            else "BUY" if trans['buysell'] == "B" \
            else "UNKNOWN"

    product = products_info['data'][str(prodId)]

    # Get ticker from Yahoo based on ISIN
    tkr = yf.Ticker(product['isin'])
    logging.info(f"[YAHOO] [GET_TICKER] ISIN {product['isin']} resolved to {tkr.ticker}")

    # Send transaction to Ghostfolio
    import_activity(
        accountId=config_dict.get('ghostfolio_account_id'), 
        currency=product['currency'], 
        dataSource="YAHOO", 
        date=defdate,  # Format: '2023-01-16T08:17:10+01:00'
        fee=trans['totalFeesInBaseCurrency'], 
        quantity=trans['quantity'], 
        symbol=tkr.ticker, 
        type=transtype, # BUY | DIVIDEND | ITEM | SELL @FIXME implement DIVIDEND
        unitPrice=trans['price']
    )
