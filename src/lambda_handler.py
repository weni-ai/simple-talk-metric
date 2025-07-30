import json
from openai import OpenAI
import sys
from get_parameter import get_parameter

OPENAI_API_KEY=get_parameter('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

def send_message(prompt):
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def build_conversation_string(messages):

    conversation_parts = []
    
    for message in messages:
        sender = message.get("sender", "")
        content = message.get("content", "")
        
        # Mapeia o sender para um formato mais legível
        if sender.lower() in ["user", "usuario", "usuário"]:
            formatted_sender = "Usuário"
        elif sender.lower() in ["bot", "chatbot", "assistant"]:
            formatted_sender = "Chatbot"
        else:
            # Mantém o sender original se não conseguir mapear
            formatted_sender = sender.capitalize()
        
        conversation_parts.append(f"[{formatted_sender}]: {content}")
    
    return "\n\n".join(conversation_parts)

def classify_text(text):
    prompt = f'''Você é um especialista em analisar se uma conversa foi apenas uma small talk com o usuário, se for apenas uma simples conversa onde o usuário não pede nada especifico, não obtem informações e não resolve nenhum problema dele significa que é uma small talk, faça isso seguido as isntruções abaixo
    instruções:
        - "true" significa que é uma small talk.
        - "false" significa que não é ums small talk
        - NÃO EXPLIQUE O PORQUE OU COMO FEZ A TAREFA APENAS FAÇA.
        - SEU OUTPUT DEVE SER APENAS OU A TAG DE "true" OU A TAG DE "false", NADA A MAIS.
        Conversa completa: \"{text}\"
        OUTPUT:
    '''
    return send_message(prompt)

def lambda_handler(event, context):
    # Agora esperamos uma lista de mensagens
    messages = event.get("messages", [])
    
    if not messages:
        return {
            'statusCode': 400,
            'body': json.dumps("Erro: entrada 'messages' está vazia ou ausente.")
        }
    
    try:
        # Constrói a string de conversa a partir das mensagens
        conversation_string = build_conversation_string(messages)
        
        # Classifica a conversa
        classification = classify_text(conversation_string)
        
        return {
            'statusCode': 200,
            'body': {
                #'conversation': conversation_string,  # Opcional: retorna a conversa montada
                'classification': classification
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Erro ao classificar: {str(e)}")
        }
