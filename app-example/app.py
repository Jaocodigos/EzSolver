"""Servidor Flask de teste para o Cloudflare Turnstile.

Usa as chaves de teste oficiais da Cloudflare, que funcionam em qualquer
domínio (inclusive localhost). Para usar chaves reais, defina as variáveis
de ambiente TURNSTILE_SITEKEY e TURNSTILE_SECRET_KEY.
"""
import os

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

# Sitekeys de teste oficiais da Cloudflare (lado do cliente)
TEST_SITEKEYS = {
    "3x00000000000000000000FF": "Força desafio interativo (visível)",
}

# Secret keys de teste oficiais da Cloudflare (lado do servidor)
TEST_SECRETS = {
    "pass": ("1x0000000000000000000000000000000AA", "Sempre valida"),
    "fail": ("2x0000000000000000000000000000000AA", "Sempre rejeita"),
    "spent": ("3x0000000000000000000000000000000AA", 'Retorna "token já usado"'),
}

REAL_SITEKEY = os.environ.get("TURNSTILE_SITEKEY")
REAL_SECRET = os.environ.get("TURNSTILE_SECRET_KEY")


@app.get("/")
def index():
    return render_template(
        "index.html",
        sitekeys=TEST_SITEKEYS,
        secrets={k: v[1] for k, v in TEST_SECRETS.items()},
        real_sitekey=REAL_SITEKEY,
        has_real_secret=bool(REAL_SECRET),
    )


@app.post("/verify")
def verify():
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    secret_choice = data.get("secret", "pass")

    if not token:
        return jsonify(ok=False, error="Token ausente no corpo da requisição."), 400

    if secret_choice == "real":

        if not REAL_SECRET:
            return jsonify(ok=False, error="TURNSTILE_SECRET_KEY não definida."), 400
        secret = REAL_SECRET

    elif secret_choice in TEST_SECRETS:
        secret = TEST_SECRETS[secret_choice][0]

    else:
        return jsonify(ok=False, error="Opção de secret inválida."), 400

    payload = {"secret": secret, "response": token}
    # IP do visitante (opcional, mas recomendado pela Cloudflare)
    payload["remoteip"] = request.headers.get("CF-Connecting-IP", request.remote_addr)

    try:
        resp = requests.post(SITEVERIFY_URL, data=payload, timeout=10)
        result = resp.json()

    except (requests.RequestException, ValueError) as exc:
        return jsonify(ok=False, error=f"Falha ao contatar a Cloudflare: {exc}"), 502

    return jsonify(ok=bool(result.get("success")), cloudflare=result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
