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

message = text2art("DEGIRO >> GHOSTFOLIO")
print("")
print(Lolcat(message))
print("")

logging.basicConfig(level=logging.INFO)

config_dict = AppConfig().get()
int_account = config_dict.get("degiro_int_account")
username = config_dict.get("degiro_username")
password = config_dict.get("degiro_password")

credentials = Credentials(
    int_account = int(int_account),
    username = username,
    password = password
)

trading_api = TradingAPI(credentials=credentials)
trading_api.connect()

# SETUP REQUEST
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

# FETCH TRANSACTIONS
transactions_history = trading_api.get_transactions_history(
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

    products_info = trading_api.get_products_info(
        request=product_request,
        raw=True
    )

    logging.debug("[DEGIRO] [PRODUCT]", products_info)

    transtype = "SELL" if trans['buysell'] == "S" \
            else "BUY" if trans['buysell'] == "B" \
            else "UNKNOWN"

    product = products_info['data'][str(prodId)]

    # Get ticker from Yahoo by ISIN
    tkr = yf.Ticker(product['isin'])
    logging.info(f"[YAHOO] [GET_TICKER] ISIN {product['isin']} resolved to {tkr.ticker}")

    accountId=config_dict.get('ghostfolio_account_id')
    currency=product['currency']
    dataSource="YAHOO" 
    date=defdate  # Format: '2023-01-16T08:17:10+01:00'
    fee=trans['totalFeesInBaseCurrency'] 
    quantity=trans['quantity']
    symbol=tkr.ticker
    type=transtype  # BUY | DIVIDEND | ITEM | SELL @FIXME implement DIVIDEND
    unitPrice=trans['price']

    # {
    #     'data': {
    #         '25144135': {
    #             'id': '25144135', 
    #             'name': 'FLOW TRADERS', 
    #             'isin': 'BMG3602E1084', 
    #             'symbol': 'FLOW', 
    #             'contractSize': 1.0, 
    #             'productType': 'STOCK', 
    #             'productTypeId': 1, 
    #             'tradable': True, 
    #             'category': 'B', 
    #             'currency': 'EUR', 
    #             'active': True, 
    #             'exchangeId': '200', 
    #             'onlyEodPrices': False, 
    #             'orderTimeTypes': ['DAY', 
    #             'GTC'], 
    #             'buyOrderTypes': ['LIMIT', 
    #             'MARKET', 
    #             'STOPLOSS', 
    #             'STOPLIMIT'], 
    #             'sellOrderTypes': ['LIMIT', 
    #             'MARKET', 
    #             'STOPLOSS', 
    #             'STOPLIMIT'], 
    #             'productBitTypes': [], 
    #             'closePrice': 22.94, 
    #             'closePriceDate': '2023-02-28', 
    #             'feedQuality': 'R', 
    #             'orderBookDepth': 0, 
    #             'vwdIdentifierType': 'issueid', 
    #             'vwdId': '612908', 
    #             'qualitySwitchable': False, 
    #             'qualitySwitchFree': False, 
    #             'vwdModuleId': 1
    #         }
    #     }
    # }

    import_activity(
        accountId=accountId, 
        currency=currency, 
        dataSource=dataSource, 
        date=date, 
        fee=fee, 
        quantity=quantity, 
        symbol=symbol, 
        type=transtype, 
        unitPrice=unitPrice
    )

    # {
    #     'transfered': False, 
    #     'quantity': 25.0, 
    #     'id': 374907108.0, 
    #     'grossFxRate': 0.0, 
    #     'totalPlusFeeInBaseCurrency': -581.5, 
    #     'price': 23.26, 
    #     'fxRate': 0.0, 
    #     'autoFxFeeInBaseCurrency': 0.0, 
    #     'date': '2023-01-16T08:17:10+01:00', 
    #     'total': -581.5, 
    #     'nettFxRate': 0.0, 
    #     'totalFeesInBaseCurrency': 0.0, 
    #     'productId': 25144135.0, 
    #     'transactionTypeId': 106.0, 
    #     'buysell': 'B', 
    #     'totalInBaseCurrency': -581.5, 
    #     'totalPlusAllFeesInBaseCurrency': -581.5
    # }

    # {
    #     'transfered': False, 
    #     'quantity': -25.0, 
    #     'id': 374907107.0, 
    #     'grossFxRate': 0.0, 
    #     'totalPlusFeeInBaseCurrency': 581.5, 
    #     'price': 23.26, 
    #     'fxRate': 0.0, 
    #     'autoFxFeeInBaseCurrency': 0.0, 
    #     'date': '2023-01-16T08:17:10+01:00', 
    #     'total': 581.5, 
    #     'nettFxRate': 0.0, 
    #     'totalFeesInBaseCurrency': 0.0, 
    #     'productId': 7218401.0, 
    #     'transactionTypeId': 106.0, 
    #     'buysell': 'S', 
    #     'totalInBaseCurrency': 581.5, 
    #     'totalPlusAllFeesInBaseCurrency': 581.5
    # }