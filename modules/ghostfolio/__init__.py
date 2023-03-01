import requests
import json
import logging
from config import AppConfig
from asciistuff import Lolcat


def get_bearer_token():
    """
    Getting the bearer token from local Ghostfolio instance.
    """
    appConfig = AppConfig()
    config_dict = appConfig.get()
    api_host = config_dict.get('ghostfolio_api_host')
    security_token = config_dict.get('ghostfolio_auth_token')
    x = requests.get(f"{api_host}/api/v1/auth/anonymous/{security_token}")
    return json.loads(x.content)['authToken']


def import_activity(accountId, currency, dataSource, date, fee, quantity, symbol, type, unitPrice):
    """Post transaction to Ghostfolio API

    Args:
        accountId (string): Id of the account in Ghostfolio
        currency (string): CHF | EUR | USD etc.
        dataSource (string): MANUAL (for type ITEM) | YAHOO
        date (ISO 8601 format): 2022-09-27 18:00:00.000
        fee (double): Fee of the activity
        quantity (double): Quantity of the activity
        symbol (string): Symbol of the activity (suitable for dataSource) (@FIXME ISIN POSSIBLE?)
        type (string): BUY | DIVIDEND | ITEM | SELL
        unitPrice (double): Price per unit of the activity

        
        POST http://localhost:3333/api/v1/import

        Body
        {
            "activities": [
                {
                "currency": "USD",
                "dataSource": "YAHOO",
                "date": "2021-09-15T00:00:00.000Z",
                "fee": 19,
                "quantity": 5,
                "symbol": "MSFT",
                "type": "BUY",
                "unitPrice": 298.58
                }
            ]
        }
    """

    postdata = {
        "activities": [
            {
                "accountId": accountId,
                "currency": currency,
                "dataSource": dataSource,
                "date": date,
                "fee": fee,
                "quantity": quantity,
                "symbol": symbol,
                "type": type,
                "unitPrice": unitPrice
            }
        ]
    }

    logging.info(f"[{date}] [{type}] [{symbol}] [{quantity}]")

    appConfig = AppConfig()
    bearer_token = get_bearer_token()
    config_dict = appConfig.get()
    api_host = config_dict.get('ghostfolio_api_host')
    url = f"{api_host}/api/v1/import"
    x = requests.post(url, json = postdata, headers = {"Authorization": f"Bearer {bearer_token}"})

    if x.status_code == 201:
        logging.info(Lolcat("[HTTP] [201] Created"))

    else:
        logging.info(Lolcat(f"[HTTP] [{x.status_code}] {json.loads(x.content)['message']}"))