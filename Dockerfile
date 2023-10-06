FROM python:3.11

WORKDIR /app

COPY requirements.txt .

COPY credentials.json /app/credentials.json

COPY token.json /app/token.json


RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD [ "chainlit", "run", "main.py"]
