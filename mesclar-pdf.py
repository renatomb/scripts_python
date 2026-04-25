# Importar a biblioteca PyPDF2
import PyPDF2

# Criar um objeto PdfFileMerger
merger = PyPDF2.PdfFileMerger()

# Iterar sobre os arquivos pdf passados como parâmetro
for pdf in sys.argv[1:]:
    # Abrir o arquivo pdf em modo binário
    file = open(pdf, "rb")
    # Adicionar o arquivo pdf ao objeto merger
    merger.append(file)

# Criar um novo arquivo chamado mesclado.pdf em modo binário
output = open("mesclado.pdf", "wb")
# Escrever o conteúdo do objeto merger no novo arquivo
merger.write(output)
# Fechar os arquivos abertos
output.close()
file.close()
