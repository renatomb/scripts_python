import os
import sys
from PyPDF2 import PdfReader, PdfWriter

# verifica se a senha foi fornecida como argumento de linha de comando
if len(sys.argv) < 2:
    print('Por favor, forneça uma senha como argumento. Ex.: python ' + sys.argv[0] + ' minha_senha')
    sys.exit()

# obtém a senha do primeiro argumento da linha de comando
password = sys.argv[1]

# define a função para remover a senha
def remove_password(filename):
    with open(filename, 'rb') as f:
        pdf = PdfReader(f)
        # verifica se o arquivo possui senha
        if pdf.is_encrypted:
            # tenta remover a senha com uma senha em branco
            pdf.decrypt(password)
            # escreve o PDF sem senha em um novo arquivo
            output = PdfWriter()
            for page in pdf.pages:
                output.add_page(page)
            with open('unencrypted_' + filename, 'wb') as out:
                output.write(out)
            print('Senha removida de ', filename)
        else:
            print('O arquivo', filename, 'não possui senha.')

# obtem a lista de arquivos PDF na pasta atual
pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]

# remove a senha de cada arquivo PDF
for filename in pdf_files:
    remove_password(filename)

