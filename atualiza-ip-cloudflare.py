import requests
import json

# Dados secretos do usuario
ZONE_ID='identificador_da_zona' 
RECORD_ID='identificador_do_registro_dns'
X_AUTH_EMAIL='email@example.com'
X_AUTH_KEY='api_key_global_da_conta'

# Obtém o IP atual da internet através do site ipinfo.io/json
response = requests.get('https://ipinfo.io/json')
ip = json.loads(response.text)['ip']

# Realiza uma requisição POST para a API do Cloudflare, atualizando o registro DNS de "sub.nome.com" com o IP obtido
url = "https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{RECORD_ID}".format(ZONE_ID=ZONE_ID, RECORD_ID=RECORD_ID)
headers = {
    'Content-Type': 'application/json',
    'X-Auth-Email': '{X_AUTH_EMAIL}'.format(X_AUTH_EMAIL=X_AUTH_EMAIL),
    'X-Auth-Key': '{X_AUTH_KEY}'.format(X_AUTH_KEY=X_AUTH_KEY)
}
data = {
    'type': 'A',
    'name': 'host.example.com',
    'content': ip,
    'ttl': 1
}
response = requests.put(url, headers=headers, json=data)

# Exibe o resultado da requisição
print(response.text)
