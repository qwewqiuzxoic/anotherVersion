list = ["upbit", "bithumb"]

##리스트 추가 후 obj에도 추가 해줄 것

obj = {
    "upbit": {
        'apiKey': '15WU8vQeQyEleAZbm1XnXJ9jzBodgXxvuWgYUyhV',
        'secret': 'Yx9TxWitNEbMdZNxlSrSx6ByNS6ySDgBKVO9Aer5',
        'enableRateLimit': True,
        'options': {
            'createMarketBuyOrderRequiresPrice': False,  ## switch off
        }
    },
    "bithumb": {
        'apiKey': '75d262801ceee2023a1b024e4e59be8c',
        'secret': 'ce0e95c32bcc8de2b8079eadd0ad9350',
        'enableRateLimit': True,
        'options': {
            'createMarketBuyOrderRequiresPrice': False,  ## switch off
        }
    }
}