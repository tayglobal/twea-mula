import kydb
import lambda_function


stage = 'dev'
db = kydb.connect('dynamodb://' + lambda_function.TABLE_MAP[stage])


def test_send_embed():
    payload = {
        "channel": "test",
        "content": "This is a test message",
        "embed": {
            "title": "Hello, Discord!",
            "description": """This is an embed message sent using the Discord API
[Artillery Kai](https://www.artillerykai.co.uk)
""",
        },
        "components": [
            {
                "type": 1,
                "components": [
                    {
                        "type": 2,
                        "label": "Click me!",
                        "style": 1,
                        "custom_id": "click_one"
                    }
                ]

            }
        ]
    }
    h = lambda_function.Handler(db, stage, payload)
    h._send_message_to_channel('test', payload)



def test_mula_add():
    payload = {
        'data': {
            'options':[
                {'name': 'who', 'type': 6, 'value': '702902250141646888'},
                {'name': 'amount', 'type': 10, 'value': 100.0},
                {'name': 'description', 'type': 3, 'value': 'foo'}
            ],
        }
    }

    lambda_function._SKIP_MESSAGE = True
    h = lambda_function.Handler(db, stage, payload)
    h.mula_add()

def test_mula_fx_set():
    payload = {
        'data': {
            'options':[
                {'name': 'ccy_pair', 'type': 3, 'value': 'GBPJPY'},
                {'name': 'fx_rate', 'type': 10, 'value': 188.71},
            ],
        }
    }

    lambda_function._SKIP_MESSAGE = True
    h = lambda_function.Handler(db, stage, payload)
    h.mula_fx_set()

def test_mula_fx_ls():
    payload = {}

    lambda_function._SKIP_MESSAGE = True
    h = lambda_function.Handler(db, stage, payload)
    h.mula_fx_ls()


def test_mula_bal():
    payload = {
        'data': {
            'options':[
                {'name': 'who', 'type': 6, 'value': '702902250141646888'},
            ],
        }
    }

    lambda_function._SKIP_MESSAGE = True
    h = lambda_function.Handler(db, stage, payload)
    h.mula_bal()

def test_mula_bal_no_arg():
    payload = {
        'data': {},
        "member": {
            "user": {
                "id": "702902250141646888"
            }
        }
    }

    lambda_function._SKIP_MESSAGE = True
    h = lambda_function.Handler(db, stage, payload)
    h.mula_bal()

if __name__ == '__main__':
    # test_send_embed()
    # test_mula_add()
    # test_mula_fx_set()
    # test_mula_fx_ls()
    # test_mula_bal()
    test_mula_bal_no_arg()
