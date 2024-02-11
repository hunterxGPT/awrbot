import sqlite3
from telethon import TelegramClient, events
import configparser

# Lire les informations d'identification à partir du fichier config.ini
config = configparser.ConfigParser()
config.read('config.ini')

api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
bot_token = config['Telegram']['bot_token']

# Créer un client Telegram avec les informations d'identification du fichier config.ini
client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

# Connexion à la base de données pour stocker les données de l'utilisateur
conn_user = sqlite3.connect('user_data.db')
c_user = conn_user.cursor()
c_user.execute('''CREATE TABLE IF NOT EXISTS users
                 (chat_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, last_name TEXT)''')

# Connexion à la base de données pour stocker les réponses
conn_responses = sqlite3.connect('bot_responses.db')
c_responses = conn_responses.cursor()
c_responses.execute('''CREATE TABLE IF NOT EXISTS responses
                     (chat_id INTEGER, message TEXT)''')

# Événement pour répondre aux messages
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('Bonjour ! Je suis votre bot Telegram.')

# Événement pour archiver les messages reçus et stocker les réponses
@client.on(events.NewMessage)
async def archive_responses(event):
    # Enregistrer les données de l'utilisateur dans la base de données
    chat_id = event.chat_id
    username = event.sender.username
    first_name = event.sender.first_name
    last_name = event.sender.last_name
    c_user.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", (chat_id, username, first_name, last_name))
    conn_user.commit()
    
    # Enregistrer le message dans la base de données des réponses
    message = event.text
    c_responses.execute("INSERT INTO responses VALUES (?, ?)", (chat_id, message))
    conn_responses.commit()

    # Répondre au message
    await event.respond(event.text)

# Lancez le client Telegram
client.run_until_disconnected()

# Fermez les connexions à la base de données lors de la déconnexion
conn_user.close()
conn_responses.close()
