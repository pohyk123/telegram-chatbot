import sqlite3
import json

conn = sqlite3.connect('ChatBot.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS chat_state (chat_id integer PRIMARY_KEY,intent text NOT NULL,context text NOT NULL,entities text NOT NULL,step integer DEFAULT 0);")

def update_chat_id_state(chat_id_state_data,chat_id): # input parameter json format
    if ('intent' in chat_id_state_data):
        c.execute("UPDATE chat_state SET intent=? WHERE chat_id=?;", (chat_id_state_data['intent'],chat_id))
    if ('context' in chat_id_state_data):
        c.execute("UPDATE chat_state SET context=? WHERE chat_id=?;", (chat_id_state_data['context'],chat_id))
    if ('entities' in chat_id_state_data):
        c.execute("UPDATE chat_state SET entities=? WHERE chat_id=?;", (chat_id_state_data['entities'],chat_id))
    if ('step' in chat_id_state_data):
        c.execute("UPDATE chat_state SET step=? WHERE chat_id=?;", (chat_id_state_data['step'],chat_id))
    conn.commit()

def reset_chat_id_state(chat_id):
    c.execute("UPDATE chat_state SET intent = '' WHERE chat_id=?;", (chat_id,))
    c.execute("UPDATE chat_state SET context = '' WHERE chat_id=?;", (chat_id,))
    c.execute("UPDATE chat_state SET entities = '' WHERE chat_id=?;", (chat_id,))
    c.execute("UPDATE chat_state SET step=0 WHERE chat_id=?;", (chat_id,))
    conn.commit()

def create_chat_id_state(chat_id):
    c.execute("INSERT INTO chat_state VALUES (?,'','','',0);",(chat_id,))
    conn.commit()

def index_chat_id_state(chat_id):
    # Retrieves query in tuple form
    chat_state = {}
    c.execute("SELECT * FROM chat_state WHERE chat_id=?;", (chat_id,))
    chat_id_data=c.fetchone()
    if (chat_id_data is not None):
        chat_state['chat_id'] = chat_id_data[0]
        chat_state['intent'] = chat_id_data[1]
        chat_state['context'] = chat_id_data[2]
        chat_state['entities'] = chat_id_data[3]
        chat_state['step'] = chat_id_data[4]

    return chat_state

def chat_id_exists(chat_id):
    c.execute("SELECT * FROM chat_state WHERE chat_id=?;", (chat_id,))
    if (c.fetchone() is None):
        return False
    else:
        return True
