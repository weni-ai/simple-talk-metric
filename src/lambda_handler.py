import json
from openai import OpenAI
import sys
from get_parameter import get_parameter
import time


def send_message(prompt):
    OPENAI_API_KEY=get_parameter('OPENAI_API_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
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
    prompt = f"""
Você é um classificador binário. Decida se a conversa abaixo está APENAS em fase de social/descoberta (sem pedido específico atendido, sem informação útil entregue, sem próximo passo executável) = "true"; ou se já há um pedido específico sendo atendido com entrega de informação concreta ou execução de ação = "false".

REGRAS — Retorne "true" quando QUALQUER um ocorrer:
- A mensagem do usuário é publicidade/anúncio/marketing, com CTAs (ex.: "Get started", links comerciais) ou texto genérico sem pedir algo concreto.
- Há somente intenção vaga de compra ("quero comprar uma airfryer", "quero uma lava-louças") e a conversa está em acolhimento/triagem: o bot só faz perguntas ("tamanho/cor/orçamento") ou diz "procurando…/analisando…".
- O bot **não** entregou itens/modelos/códigos específicos, **nem** disponibilidade, **nem** uma lista objetiva de promoções **nem** um próximo passo executável (criar pedido, agendar, enviar orçamento, link de compra específico).
- A conversa termina sem o usuário responder às perguntas de triagem.
- Mensagens automáticas do bot como "procurando…", "analisando…" sem resultado também contam como "true".
- Observação: preços genéricos do tipo "a partir de R$ X" **sem** associar a um item/modelo específico **NÃO** contam como informação concreta.

Retorne "false" SOMENTE se pelo menos UM ocorrer:
- O usuário faz um pedido específico (ex.: "quais promoções desta semana?") **e** o bot entrega o conteúdo pedido (lista de promoções com itens/valores/condições).
- O bot fornece recomendações concretas (≥1 produto com nome/modelo/código) ou executa um próximo passo (pedido criado, agendamento feito, orçamento enviado, link direto de compra de um item específico).
- Há resolução clara do objetivo do usuário.

FORMATO DE SAÍDA:
- Responda APENAS com "true" ou "false" em minúsculas, nada mais.

CONVERSA:
{text}
"""
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
