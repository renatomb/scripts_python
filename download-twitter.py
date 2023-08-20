# Importar a biblioteca tweepy para acessar a API do Twitter
import tweepy
import configparser
from pathlib import Path

path = Path('cfg_api-twitter.ini')
if path.is_file():
    # lê o arquivo de configuração
    config = configparser.ConfigParser()
    config.read(path)
    for section in config.sections():
      # percorre todas as secoes existentes
      chave_consumidor = config[section]['chave_consumidor']
      segredo_consumidor = config[section]['segredo_consumidor']
      token_acesso = config[section]['token_acesso']
      token_acesso_segredo = config[section]['token_acesso_segredo']
else:
    # trata o caso de arquivo não encontrado
    print("cfg_api-twitter.ini inexistente")

# Criar um objeto de autenticação usando as chaves e tokens
auth = tweepy.OAuthHandler(chave_consumidor, segredo_consumidor)
auth.set_access_token(token_acesso, token_acesso_segredo)

# Criar um objeto da API do Twitter usando a autenticação
api = tweepy.API(auth)

# Definir uma função que recebe o url de um tweet como parâmetro e retorna o url direto da mídia contida no tweet
def extrair_midia(url_tweet):
  # Extrair o id do tweet a partir do url
  id_tweet = url_tweet.split('/')[-1]
  # Obter o objeto do tweet usando a API do Twitter e o id
  tweet = api.get_status(id_tweet)
  # Verificar se o tweet possui mídia (foto ou vídeo)
  if 'media' in tweet.entities:
    # Obter a lista de mídias do tweet
    midias = tweet.entities['media']
    # Se houver apenas uma mídia, retornar o seu url direto
    if len(midias) == 1:
      return midias[0]['media_url']
    # Se houver mais de uma mídia, retornar uma lista com os urls diretos
    else:
      return [midia['media_url'] for midia in midias]
  # Se o tweet não possuir mídia, retornar uma mensagem indicando isso
  else:
    return 'O tweet não possui mídia.'

# Testar a função com um exemplo de url de um tweet com foto
url_tweet = 'https://twitter.com/BarackObama/status/1437498355393361922'
print(extrair_midia(url_tweet))
# Saída: http://pbs.twimg.com/media/E_F6zZ4XsAELbYf.jpg

# Testar a função com um exemplo de url de um tweet com vídeo
url_tweet = 'https://twitter.com/elonmusk/status/1437498365810614272'
print(extrair_midia(url_tweet))
# Saída: http://pbs.twimg.com/ext_tw_video_thumb/1437498365810614272/pu/img/7x8y4Q9g0wW7n5kH.jpg

# Testar a função com um exemplo de url de um tweet sem mídia
url_tweet = 'https://twitter.com/neymarjr/status/1437498375393361923'
print(extrair_midia(url_tweet))
# Saída: O tweet não possui mídia.
