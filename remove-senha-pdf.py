import os
from PyPDF2 import PdfFileReader, PdfFileWriter

# define a função para remover a senha
def remove_password(filename):
    with open(filename, 'rb') as f:
        pdf = PdfFileReader(f)
        # verifica se o arquivo possui senha
        if pdf.isEncrypted:
            # tenta remover a senha com uma senha em branco
            pdf.decrypt('')
            # escreve o PDF sem senha em um novo arquivo
            output = PdfFileWriter()
            for i in range(pdf.getNumPages()):
                output.addPage(pdf.getPage(i))
            with open('unencrypted_' + filename, 'wb') as out:
                output.write(out)
            print('Senha removida de ', filename)
        else:
            print('O arquivo', filename, 'não possui senha.')

# obtem a lista de arquivos PDF na pasta atual
pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]

# remove a senha de cada arquivo PDF
for filename in pdf_files:
    remove_password(filename)

