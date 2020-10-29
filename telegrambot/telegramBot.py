import telegram

class telegramBot():
    def __init__(self, token="1334550193:AAGJ3dqpfzNfr148zPoNjWy0ZgouVhXpFu4"):
        self.token = token
        self.bot = telegram.Bot(token= self.token)


        '''
        print(self.bot)
        updates = self.bot.getUpdates()
        for i in self.bot.getUpdates():
            print(i.message)
        '''

    def send_mess(self, text):
        self.bot.sendMessage(chat_id='1086360547', text=text)


