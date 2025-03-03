from flask import Flask, jsonify
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/produtos', methods=['GET'])
def obter_produtos():
    """Carrega os produtos do arquivo JSON e os retorna como resposta"""
    try:
        # Verifica se o arquivo existe
        if not os.path.exists("produtos_hayamax.json"):
            return jsonify({"error": "Arquivo de produtos não encontrado."}), 404
        
        # Carrega o arquivo JSON com os produtos
        with open("produtos_hayamax.json", "r", encoding="utf-8") as f:
            produtos = json.load(f)
        
        # Retorna os produtos no formato JSON
        return jsonify(produtos), 200
    except Exception as e:
        print(f"Erro ao carregar o arquivo JSON: {e}")
        return jsonify({"error": "Erro ao carregar os produtos."}), 500

if __name__ == '__main__':
    app.run(debug=True)
