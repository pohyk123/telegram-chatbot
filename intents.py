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
                message+='Here are the train arrival estimates near your location.\n'
                message+='\n'
                nearbyTubes = tfl.getNearbytubes(userLocation)
                for nearbyTube in nearbyTubes:
                    message+='<i>'
                    message+=nearbyTube['commonName']
                    message+='</i> ('
                    message+=str(nearbyTube['dist'])
                    message+=' metres away)'
                    message+='\n'
                    lines = tfl.getLinesServingStation(nearbyTube['id'])
                    trainArrivals = tfl.getNextTrainArrivals(nearbyTube['id'],lines)
                    for i in range(len(trainArrivals)):
                        message+='<b>['
                        message+=trainArrivals[i]['line']
                        message+=' line] </b>- '
                        for j in range(len(trainArrivals[i]['next_arrival'])):
                            message+=str(trainArrivals[i]['next_arrival'][j])
                            message+=' min ('
                            message+=trainArrivals[i]['towards'][j]
                            message+='), '
                        message+='\n'
                    message+='\n'

                reply_markup = '{"remove_keyboard":true}'
                # Last step of intent flow
                intent_flow_end = True
                endOfFlow(chat_id)
            except Exception as e:
                print(e)
                message = 'Invalid step input. Resetting all contexts & steps.'
                reply_markup = '{"remove_keyboard":true}'
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
            message+='Location required; please click on button below. Please be patient while the server attempts to retrieve incoming train timings.'
            reply_markup = '{"keyboard":[[{"text":"Send current location","request_location":true}]],"one_time_keyboard":true}'
            step+=1

    elif(intent == 'display menu'):
        message+='Hello there! Here are some available options for you!'
        reply_markup='{"inline_keyboard":[[{"text":"Get Tube Status","callback_data":"Get tube status"}],[{"text":"Get Tube Timings","callback_data":"Get tube timings"}]]}'

    else:
        message+='No matching intents. Please key in a valid request.'
        reply_markup = '{"remove_keyboard":true}'
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
        if ('status' in message or 'update' in message):
            intent = 'Retrieve Tube Status'
        if ('time' in message or 'timings' in message):
            intent = 'Retrieve next Tube Timings'
    if ('hi' in message or 'hey' in message or 'hello' in message or 'help' in message):
        intent = 'display menu'

    entities = message.split()
    components = {'context':context,'intent':intent,'entities':entities}
    return components
