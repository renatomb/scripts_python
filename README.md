# Scripts Python diversos

Este repositório contém vários scripts utilitários em Python. Este README descreve cada script, dependências, exemplos de uso e observações importantes.

Sumário
- Requisitos globais
- Instalação rápida
- Descrição dos scripts
  - analisador-de-voz.py
  - atualiza-ip-cloudflare.py
  - bcrypt-gen.py
  - mesclar-pdf.py
  - remove-senha-pdf.py
  - sqlite_to_mysql.py
- Boas práticas e melhorias sugeridas
- Como contribuir / abrir pull request
- Licença

Requisitos globais
- Python 3.8+ (recomendado 3.10+)
- pip
- É fortemente recomendado usar um ambiente virtual (venv/virtualenv).

Instalação rápida
1. Clone o repositório e entre na pasta:
   git clone https://github.com/renatomb/scripts_python.git
   cd scripts_python

2. (Opcional) Crie e ative um ambiente virtual:
   python -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .\.venv\Scripts\activate    # Windows

3. Instale dependências quando necessário (os scripts individuais indicam dependências). Exemplo:
   pip install numpy librosa scipy requests PyPDF2 bcrypt

Descrição dos scripts

1) analisador-de-voz.py
- Objetivo
  Faz uma análise acústica de um arquivo de áudio (voz), extraindo métricas como duração, faixa dinâmica, SNR estimado, f0 (fundamental), jitter, shimmer, centroid espectral, rolloff, MFCCs, razão de sibilância e estimativa de palavras por minuto (WPM). Também tenta extrair formantes usando LPC.

- Dependências
  numpy, librosa, scipy

- Uso
  python analisador-de-voz.py caminho/para/audio.mp3

  Se nenhum argumento for passado, tenta abrir "oracao arcanjo miguel.mp3" por padrão.

- Saída
  Gera um JSON no stdout com os campos:
  - sample_rate, duration_sec, dynamic_range_db, snr_db_estimate
  - f0_mean_hz, f0_min_hz, f0_max_hz, jitter_local, shimmer_local
  - spectral_centroid_mean_hz, spectral_rolloff_85_mean_hz, mfcc_means
  - sibilance_ratio_5_8k, voiced_unvoiced_ratio, syllables_est, syll_per_sec, wpm_est
  - formants (F1, F2, F3 ou erro)

- Observações / limitações
  - Precisão depende da qualidade do áudio e das configurações de frame/hop.
  - Requer arquivos mono ou que sejam carregáveis pelo librosa.
  - A estimativa de sílabas / WPM é aproximada; pode exigir ajuste dos parâmetros de detecção de onsets.
  - Recomenda-se fornecer arquivos limpos (com pouco ruído) para melhores medidas de f0/jitter/shimmer.

2) atualiza-ip-cloudflare.py
- Objetivo
  Atualiza registros DNS de zonas no Cloudflare com o IP público atual (IPv4 / IPv6) para múltiplas seções definidas em um arquivo de configuração INI.

- Dependências
  requests

- Arquivo de configuração (cfg_atualiza-ip.ini)
  O script espera um arquivo `cfg_atualiza-ip.ini` na pasta atual. Cada seção representa um host a ser atualizado. Exemplo de seção:
  [meuservidor_ipv4]
  zone_id = <ZONE_ID>
  record_id = <RECORD_ID>
  host_record = sub.exemplo.com
  x_auth_email = seu-email@exemplo.com
  x_auth_key = sua_chave_api_global

  Observação: o script detecta se a seção termina com "ipv4" ou "ipv6" para obter o IP via serviços diferentes e setar o tipo de registro (A ou AAAA).

- Uso
  python atualiza-ip-cloudflare.py

- Saída
  Imprime a resposta JSON da API do Cloudflare para cada seção (status da atualização).

- Observações / segurança
  - Não inclua chaves sensíveis em repositórios públicos. Use variáveis de ambiente ou um arquivo de configuração protegido.
  - Verifique permissões da chave Cloudflare (X-Auth-Key) e formatos de zone_id/record_id.

3) mesclar-pdf.py
- Objetivo
  Mesclar vários arquivos PDF em um único arquivo chamado `mesclado.pdf`.

- Dependências
  PyPDF2 (pip install PyPDF2)

- Uso
  python mesclar-pdf.py arquivo1.pdf arquivo2.pdf arquivo3.pdf
  Resultado: arquivo `mesclado.pdf` contendo todas as páginas na ordem passada.

- Observações
  - O script pressupõe que o PDF exista e que `sys.argv` contenha os caminhos; se nenhum arquivo for passado, nada acontece (pode gerar erro).
  - Sugestão: adicionar verificação de argumentos, mensagens de erro e fechar todos os arquivos abertos corretamente.

4) remove-senha-pdf.py
- Objetivo
  Remove a senha de arquivos PDF encriptados (descriptografa) usando uma senha fornecida via argumento CLI, processando todos os PDFs na pasta atual e gravando uma cópia sem senha com o prefixo `unencrypted_`.

- Dependências
  PyPDF2

- Uso
  python remove-senha-pdf.py minha_senha

- Saída
  Para cada PDF encriptado, cria `unencrypted_<nome>.pdf` sem senha e imprime mensagem de sucesso.

- Observações
  - O script tenta `pdf.decrypt(password)` com a senha passada. Se a senha estiver correta, grava a versão sem senha.
  - Confirme se você tem permissão para modificar os PDFs e faça backups antes.

5) sqlite_to_mysql.py
- Objetivo
  Exportar a estrutura e os dados de um banco SQLite para um arquivo SQL com sintaxe aproximada para MySQL. O script converte tipos básicos (INTEGER->INT, REAL->FLOAT, TEXT->VARCHAR(255), BLOB->BLOB) e gera INSERTs.

- Dependências
  módulo padrão sqlite3 (Python)

- Uso
  python sqlite_to_mysql.py banco.sqlite saida_mysql.sql

- Observações / limitações
  - A conversão de tipos é simplificada. Revise as colunas VARCHAR(255) e ajuste tamanhos conforme necessário.
  - Constraints, chaves primárias/auto-increment e índices são tratados de forma limitada: o script só lê informações de PRAGMA table_info; não recria triggers, índices compostos, foreign keys, ou outras propriedades avançadas.
  - Recomenda-se revisar manualmente o SQL gerado antes de importá-lo em um servidor MySQL.
