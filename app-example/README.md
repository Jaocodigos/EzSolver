# Cloudflare Turnstile - Exemplo de uso e contorno com EzSolver (Flask)

Página local para testar o widget do Turnstile com o resolver desenvolvido pelo **ismoiloff**,
usando as **chaves de teste oficiais da Cloudflare** (`localhost`).

## Como rodar(pip ou uv)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    |    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python app-example.py
```

OU

```bash
uv venv
uv add -r app-example/requirements.txt
uv add nodriver
```

Abra http://127.0.0.1:5000

Requisitos: **Python 3.9+** e acesso à internet (o navegador carrega o script da
Cloudflare e o servidor chama a API `siteverify`).

## Como usar a página

1. Escolha uma **sitekey** (comportamento do widget).
2. Escolha uma **secret key** (comportamento da validação no servidor).
3. Aguarde o widget gerar o token e clique em **Enviar para validação**.

## Combinações úteis

| Sitekey | Secret | Resultado esperado |
|---|---|---|
| `1x00000000000000000000AA` (passa) | Sempre valida | Sucesso |
| `2x00000000000000000000AB` (falha) | Sempre rejeita | Falha |
| `1x00000000000000000000AA` (passa) | "Token já usado" | `timeout-or-duplicate` |
| `1x00000000000000000000BB` (invisível) | Sempre valida | Sucesso, sem widget visível |
| `3x00000000000000000000FF` (interativo) | Sempre valida | Exige clique no desafio |

As sitekeys de teste geram o token falso `XXXX.DUMMY.TOKEN.XXXX`, aceito apenas
pelas secret keys de teste. Uma secret key real rejeita esse token.

## Usando o EzSolver

Usando chamada única via arquivo:

```bash
python solve.py "sitekey" "site-url" # python solve.py 3x00000000000000000000FF http://127.0.0.1:5000
```

Subindo um serviço para chamadas constantes:

Linux
```bash
export CHROME_PATH=caminho-do-browser-executavel
export PORT=9000 
export MAX_WORKERS=2 # recomendado para maquinas mais fracas
python service.py
```

No Windows (PowerShell): `$env:CHROME_PATH="..."`.

Fazendo requisições para o serviço:

```bash
curl -s -X POST http://127.0.0.1:9000/solve \
  -H "Content-Type: application/json" \
  -d '{"sitekey":"3x00000000000000000000FF","siteurl":"http://127.0.0.1:5000"}'
```

## Estrutura

```
app-example/
├── app.py              # servidor Flask (rotas / e /verify)
├── requirements.txt
└── templates/
    └── index.html      # frontend com o widget
```
