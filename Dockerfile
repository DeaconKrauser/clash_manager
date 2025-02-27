# Use uma imagem Python oficial como base
FROM python:3.9-slim-buster

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo requirements.txt
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Expõe a porta 5000 (a porta padrão do Flask em desenvolvimento)
EXPOSE 5000

# Define o comando para executar a aplicação
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]