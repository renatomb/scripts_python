import requests
import json
import configparser
from pathlib import Path

def atualizarip(tipo):
    ZONE_ID = config[tipo]['zone_id']
    RECORD_ID = config[tipo]['record_id']
    HOST_RECORD = config[tipo]['host_record']
    X_AUTH_EMAIL = config[tipo]['x_auth_email']
    X_AUTH_KEY = config[tipo]['x_auth_key']
    print("Buscando "+tipo+"...")
    if tipo == "ipv4":
        # Obtém o IPv4 atual da internet através do site ipinfo.io/json
        response = requests.get('https://ipinfo.io/json')
        HOST_TYPE = 'A'
    else:
        # Obtém o IPv6 atual da internet através do site https://ipv6.seeip.org/jsonip
        response = requests.get('https://ipv6.seeip.org/jsonip')
        HOST_TYPE = 'AAAA'
    ip = json.loads(response.text)['ip']
    # Realiza uma requisição POST para a API do Cloudflare, atualizando o registro DNS com o IP obtido
    url = "https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{RECORD_ID}".format(ZONE_ID=ZONE_ID, RECORD_ID=RECORD_ID)
    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Email': '{X_AUTH_EMAIL}'.format(X_AUTH_EMAIL=X_AUTH_EMAIL),
        'X-Auth-Key': '{X_AUTH_KEY}'.format(X_AUTH_KEY=X_AUTH_KEY)
    }
    data = {
        'type': '{HOST_TYPE}'.format(HOST_TYPE=HOST_TYPE),
        'name': '{HOST_RECORD}'.format(HOST_RECORD=HOST_RECORD),
        'content': ip,
        'ttl': 1
    }
    response = requests.put(url, headers=headers, json=data)
    print(response.text)


path = Path('cfg_atualiza-ip.ini')
if path.is_file():
    # lê o arquivo de configuração
    config = configparser.ConfigParser()
    config.read(path)
    # verifica se existe configuracao de ipv4
    if config.has_section('ipv4'):
        atualizarip("ipv4")      
    else:
        # trata o caso de seção não encontrada
        print("Nenhum ipv4 a atualizar")
    # verifica se existe configuracao de ipv6
    if config.has_section('ipv6'):
        atualizarip("ipv6")
    else:
        # trata o caso de seção não encontrada
        print("Nenhum ipv6 a atualizar")
else:
    # trata o caso de arquivo não encontrado
    print("cfg_atualiza-ip.ini inexistente")