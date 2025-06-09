from flask import Flask, render_template, request
import requests
import urllib.parse

app = Flask(__name__)

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
    mensagem = mensagem.lower()

    if mensagem.startswith("me traduza"):
        # Ex: "me traduza eu te amo para inglês"
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

    elif "oi" in mensagem or "olá" in mensagem:
        return "Olá! Como posso te ajudar hoje?"

    elif "tchau" in mensagem:
        return "Tchau! Até logo!"

    else:
        return "Desculpe, ainda estou aprendendo. Pergunte outra coisa!"

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
