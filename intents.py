import tfl
import dbManager
import json
import re

intents_list = ['Retrieve Tube Status','Retrieve next Tube Timings']

# Flow starts as new intent or existing flow.
def getIntentResponse(message,chat_id):
    if (checkChatExists(chat_id) is False):
        print("Chat ID does not exist, creating new chat ID query.")
        createNewChat(chat_id)
    step = getCurrentChatStep(chat_id)
    components = classifyMessageParts(message)
    # Initial Layer
    if (step == 0):
        context = components['context']
        intent = components['intent']
        entities = components['entities']
        response = processNewIntent(intent,context,entities,chat_id)

    else:
        entities =  components['entities']
        intent = getCurrentChatIntent(chat_id)
        response = processExistingIntent(step,intent,entities,chat_id)

    return response


def processExistingIntent(step,intent,entities,chat_id):
    intent_flow_end = False
    message = ''
    reply_markup = ''
    success = True
    if (intent == 'Retrieve next Tube Timings'):
        if (step == 1):
            try:
                # location json data is sent as string
                entitiesTemp = ' '.join(entities)
                entitiesTemp=entitiesTemp.replace("'", '"')
                userLocation = json.loads(entitiesTemp)
                # use tfl api to find out next tube timings
                message+='Here are the train arrival estimates near your location.'
                message+='\n'
                nearbyTubes = tfl.getNearbytubes(userLocation)
                for nearbyTube in nearbyTubes:
                    message+=nearbyTube['commonName']
                    message+=' ('
                    message+=str(nearbyTube['dist'])
                    message+=' metres away)'
                    message+='\n'
                    lines = tfl.getLinesServingStation(nearbyTube['id'])
                    trainArrivals = tfl.getNextTrainArrivals(nearbyTube['id'],lines)
                    for i in range(len(trainArrivals)):
                        message+=trainArrivals[i]['line']
                        message+=' line - '
                        message+=trainArrivals[i]['next_arrival']
                        message+=' minutes\n'

                    message+='\n\n'

                reply_markup = '{"remove_keyboard":true}'
                # Last step of intent flow
                intent_flow_end = True
                endOfFlow(chat_id)
            except Exception as e:
                print(e)
                message = 'Invalid step input. Resetting all contexts & steps.'
                success = False
                endOfFlow(chat_id)

    entities = ' '.join(entities)
    if (success and intent_flow_end == False):
        update_chat_id_state({'intent':intent,'step':step,'entities':entities},chat_id)
    response = {'message':message,'reply_markup':reply_markup}
    return response


def processNewIntent(intent,context,entities,chat_id):
    reply_markup = ''
    message = ''
    success = True
    step=0

    # hard code logic
    if(context == 'tube'):
        if (intent == 'Retrieve Tube Status'):
            tubeStatus = tfl.getTubeStatus()
            for line in tubeStatus:
                message+=line['id']+': '+line['status']
                message+='\n'
        elif (intent == 'Retrieve next Tube Timings'):
            message+='Location required; please click on button below.'
            reply_markup = '{"keyboard":[[{"text":"Send current location","request_location":true}]],"one_time_keyboard":true}'
            step+=1
    else:
        message+='No matching intents. Please key in a valid request.'
        success = False
        endOfFlow(chat_id)

    entities = ' '.join(entities)
    if (success):
        update_chat_id_state({'intent':intent,'context':context,'entities':entities,'step':step},chat_id)
    response = {'message':message,'reply_markup':reply_markup}
    return response

def checkChatExists(chat_id):
    return dbManager.chat_id_exists(chat_id)

def getCurrentChatStep(chat_id):
    step = (dbManager.index_chat_id_state(chat_id))['step']
    return step

def createNewChat(chat_id):
    dbManager.create_chat_id_state(chat_id)

def getCurrentChatContext(chat_id):
    context = (dbManager.index_chat_id_state(chat_id))['context']
    return context

def getCurrentChatIntent(chat_id):
    intent = (dbManager.index_chat_id_state(chat_id))['intent']
    return intent

def getCurrentChatEntities(chat_id):
    entities = (dbManager.index_chat_id_state(chat_id))['entities']
    return entities

def update_chat_id_state(new_state,chat_id):
    dbManager.update_chat_id_state(new_state,chat_id)

def endOfFlow(chat_id):
    # Reset intent flow by updating database
    dbManager.reset_chat_id_state(chat_id)

# Deciphers an intent
def classifyMessageParts(message):
    context = 'Context does not exist.'
    intent = 'Intent does not exist.'
    entities = []
    if ('tube' in message):
        context = 'tube'
        if ('status' in message):
            intent = 'Retrieve Tube Status'
        if ('time' in message or 'timings' in message):
            intent = 'Retrieve next Tube Timings'

    entities = message.split()
    components = {'context':context,'intent':intent,'entities':entities}
    return components
