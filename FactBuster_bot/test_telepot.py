import telepot

token = '417979782:AAFv5IMcPNYhKjQWX8ZoN6LO__P1nByauoQ'
TelegramBot = telepot.Bot(token)
#print(TelegramBot.getMe())

#print(TelegramBot.getUpdates(382016792+1))
data = TelegramBot.getUpdates(382016792+1)
print(data.text)
