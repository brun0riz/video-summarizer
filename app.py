import pytube
import ffmpeg
import openai
import sys
import os
import time

# CHAVE PARA CONSEGUIR USAR OS SERVIÇOS DO OPENAI
openai.api_key = "sua_chave_api"  # Lembre-se de substituir pela sua chave ou armazená-la de forma segura.

# BAIXAR O VÍDEO DO YOUTUBE
url = sys.argv[1]  # Pega a URL do vídeo baseada nos argumentos passados pela linha de comando
file_name = 'audio.wav'  # Define o nome do arquivo para salvar o áudio

success = False
attempts = 3  # Número de tentativas para baixar o vídeo

for attempt in range(attempts):
    try:
        yt = pytube.YouTube(url)  # Cria um objeto YouTube com a URL fornecida
        stream = yt.streams.filter(only_audio=True).first()  # Filtra apenas streams de áudio

        if stream is None:
            raise Exception("Nenhum stream de áudio disponível.")

        # Baixa o áudio do vídeo
        stream.download(filename='audio.mp4')
        success = True
        break  # Sai do loop se o download for bem-sucedido
    except Exception as e:
        print(f"Tentativa {attempt + 1} falhou: {e}")
        time.sleep(3)  # Aguarda 3 segundos antes de tentar novamente

if not success:
    print("Falha ao baixar o áudio após múltiplas tentativas.")
    sys.exit(1)

# CONVERTER O ÁUDIO PARA WAV
ffmpeg.input('audio.mp4').output(file_name, format='wav', loglevel="error").run()

# TRANSCRIÇÃO USANDO O WHISPER
with open(file_name, "rb") as audio_file:
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

print("Transcrição completa")

# GERAR O RESUMO USANDO O GPT
response = openai.ChatCompletion.create(
    model="gpt-4",  # Você pode usar gpt-4 ou gpt-3.5-turbo
    messages=[
        {"role": "system", "content": "Você é um assistente que resume transcrições de áudio"},
        {"role": "user", "content": f"Faça um resumo do seguinte texto: {transcript['text']}"}
    ]
)

# Pegando o conteúdo do resumo
resumo = response['choices'][0]['message']['content']
print("Resumo do vídeo: ")
print(resumo)

# Removendo arquivos temporários
os.remove('audio.mp4')
os.remove('audio.wav')
