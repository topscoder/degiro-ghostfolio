import requests
import json

def get_bearer_token(api_host="http://localhost:3333", security_token=""):
    """
    You can get the Bearer Token via GET http://localhost:3333/api/v1/auth/anonymous/<INSERT_SECURITY_TOKEN_OF_ACCOUNT> 
    or curl -s http://localhost:3333/api/v1/auth/anonymous/<INSERT_SECURITY_TOKEN_OF_ACCOUNT>.
    """
    x = requests.get(f"{api_host}/api/v1/auth/anonymous/{security_token}")
    return json.loads(x.content)['authToken']


def import_activity(bearer_token, accountId, currency, dataSource, date, fee, quantity, symbol, type, unitPrice):
    """Post transaction to Ghostfolio API

    Args:
        bearer_token (string): _description_
        accountId (_type_): _description_
        currency (_type_): _description_
        dataSource (_type_): _description_
        date (_type_): _description_
        fee (_type_): _description_
        quantity (_type_): _description_
        symbol (_type_): _description_
        type (_type_): _description_
        unitPrice (_type_): _description_

        accountId	string (optional)	Id of the account
        currency	string	CHF | EUR | USD etc.
        dataSource	string	MANUAL (for type ITEM) | YAHOO
        date	string	Date in the format ISO-8601
        fee	number	Fee of the activity
        quantity	number	Quantity of the activity
        symbol	string	Symbol of the activity (suitable for dataSource)
        type	string	BUY | DIVIDEND | ITEM | SELL
        unitPrice	number	Price per unit of the activity

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
    activity = {
        "currency": "USD",
        "dataSource": "YAHOO",
        "date": "2021-09-15T00:00:00:00.000Z",
        "fee": 19,
        "quantity": 3,
        "symbol": "T",
        "type": "BUY",
        "unitPrice": 13.37
    }

    url = f"http://192.168.1.49:3333/api/v1/import"
    x = requests.post(url, json = {"activities": [activity]}, headers = {"Authorization": f"Bearer {bearer_token}"})
    print(x)