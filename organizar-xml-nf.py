# -*- coding: utf-8 -*-
import os
import shutil
import xml.etree.ElementTree as ET
import argparse
import sys  # Adicionado para controle de exit codes

# Configurar argumentos da linha de comando
parser = argparse.ArgumentParser(description='Script para organizar arquivos XML de NFCe por ano e mes.')
parser.add_argument('source_dir', help='Diretorio fonte dos arquivos XML')
parser.add_argument('target_base', help='Diretorio base de destino')
args = parser.parse_args()

# Diretórios a partir dos argumentos
source_dir = args.source_dir
target_base = args.target_base

# Namespace do XML
namespace = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

# Função para extrair ano e mês da data de emissão
def extract_year_month(dhEmi_text):
    date_part = dhEmi_text.split('T')[0]  # Pega a parte da data antes de 'T'
    year, month, _ = date_part.split('-')
    return year, month

# Iterar sobre os arquivos XML no diretório fonte
for filename in os.listdir(source_dir):
    if filename.endswith('.xml'):
        file_path = os.path.join(source_dir, filename)
        
        try:
            # Parsear o XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Encontrar a tag dhEmi
            dhEmi = root.find('.//nfe:dhEmi', namespace)
            if dhEmi is not None:
                year, month = extract_year_month(dhEmi.text)
                
                # Criar o caminho do diretório de destino
                target_dir = os.path.join(target_base, year, month)
                os.makedirs(target_dir, exist_ok=True)
                
                # Caminho completo do arquivo de destino
                target_file = os.path.join(target_dir, filename)
                
                # Verificar se o arquivo já existe no destino
                if not os.path.exists(target_file):
                    # Copiar o arquivo
                    shutil.copy2(file_path, target_file)
                    print(f'Arquivo {filename} copiado para {target_dir}')
                else:
                    print(f'Arquivo {filename} ja existe em {target_dir}')
            else:
                print(f'Tag dhEmi nao encontrada no arquivo {filename}')
        except ET.ParseError as e:
            print(f'Erro ao parsear o arquivo {filename}: {e}')
            sys.exit(1)  # Sai com erro em caso de falha no parsing
        except Exception as e:
            print(f'Erro ao processar o arquivo {filename}: {e}')
            sys.exit(1)  # Sai com erro para outras exceções

# Indicação de sucesso ao final
print("Execucao concluida com sucesso.")
sys.exit(0)  # Sai com sucesso