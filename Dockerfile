FROM python:3.10-slim

WORKDIR /app

COPY environment.yml ./
RUN pip install --upgrade pip \
    && pip install jupyter numpy pandas requests flask matplotlib openai google-generativeai

COPY . .

RUN npm create vite@latest frontend -- --template react

CMD ["bash"]

