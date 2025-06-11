from flask import Flask, render_template, request
import requests
import urllib.parse
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from transformers import AutoModelForCausalLM, AutoTokenizer


app = Flask(__name__)

# Carregar o modelo e o tokenizer do DialoGPT
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def traduzir_lingva(texto, source_lang, target_lang):
    texto_escapado = urllib.parse.quote(texto)
    url = f"https://lingva.ml/api/v1/{source_lang}/{target_lang}/{texto_escapado}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        resultado = response.json()
        return resultado.get("translation", "Erro: resposta sem tradução")
    except Exception as e:
        return f"Erro: {e}"

def responder_como_chatbot(mensagem):
    mensagem = mensagem.lower().strip()

    # Comando para tradução
    if mensagem.startswith("me traduza"):
        partes = mensagem.split("para")
        if len(partes) == 2:
            texto = partes[0].replace("me traduza", "").strip()
            destino = partes[1].strip()
            idioma_destino = mapear_idioma(destino)
            if idioma_destino:
                idioma_origem = 'pt' if idioma_destino == 'en' else 'en'
                return traduzir_lingva(texto, idioma_origem, idioma_destino)
            else:
                return "Idioma de destino não reconhecido."
        else:
            return "Formato inválido. Tente: me traduza [texto] para [idioma]"

    # Respostas básicas de conversa
    elif any(p in mensagem for p in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]):
        return "Olá! Como posso te ajudar hoje?"

    elif "como você está" in mensagem or "tudo bem" in mensagem:
        return "Estou ótimo, obrigado por perguntar! E você?"

    elif "qual seu nome" in mensagem:
        return "Eu sou um chatbot educativo criado para ajudar você!"

    elif "obrigado" in mensagem or "obrigada" in mensagem:
        return "De nada! Estou aqui para ajudar sempre que precisar."

    elif "tchau" in mensagem or "até logo" in mensagem:
        return "Tchau! Foi bom conversar com você."

    elif "quem descobriu o brasil" in mensagem:
        return "O Brasil foi descoberto pelo navegador português Pedro Álvares Cabral, em 1500."

    elif "qual a capital do brasil" in mensagem:
        return "A capital do Brasil é Brasília."

    else:
        # Usar DialoGPT para respostas mais complexas
        try:
            # Codificar a nova entrada do usuário, adicionar o token de fim de string e retornar os tensores pt
            new_user_input_ids = tokenizer.encode(mensagem + tokenizer.eos_token, return_tensors='pt')

            # Gerar uma resposta
            chat_history_ids = model.generate(new_user_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

            # Decodificar a resposta e retornar
            response = tokenizer.decode(chat_history_ids[:, new_user_input_ids.shape[-1]:][0], skip_special_tokens=True)
            return response
        except Exception as e:
            return f"Erro na IA: {e}"

def mapear_idioma(nome):
    nome = nome.lower()
    if nome in ['ingles', 'english', 'en']:
        return 'en'
    elif nome in ['portugues', 'português', 'pt']:
        return 'pt'
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    texto_usuario = None
    resposta_bot = None

    if request.method == 'POST':
        texto_usuario = request.form['texto']
        resposta_bot = responder_como_chatbot(texto_usuario)

    return render_template('index.html', texto_usuario=texto_usuario, traducao=resposta_bot)

if __name__ == '__main__':
    app.run(debug=True)
