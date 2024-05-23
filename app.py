from flask import Flask, request, render_template, jsonify
from groq import Groq
import json

app = Flask(__name__)
client = Groq(api_key="")

# Archivo para almacenar las conversaciones
conversations_file = 'conversations.json'


# Función para cargar las conversaciones desde el archivo JSON
def load_conversations():
    try:
        with open(conversations_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(e)
        return []


# Función para guardar las conversaciones en el archivo JSON
def save_conversations(conversations):
    try:
        with open(conversations_file, 'w') as file:
            json.dump(conversations, file, indent=4)
    except Exception as e:
        print(e)

@app.route('/', methods=['GET', 'POST'])
def base():
    if request.method == 'POST':
        data = request.get_json()  # Obtener datos JSON de la solicitud
        user_message = data.get('message', '')
        response = None

        # Cargar las conversaciones existentes desde el archivo JSON
        conversations = load_conversations()

        if user_message:
            # Agregar el mensaje del usuario al historial de conversaciones
            conversations.append({"role": "user", "content": user_message})

            try:
                # Crear el historial de mensajes a enviar al chatbot
                messages = [{"role": "system", "content": "You only speak spanish"}] + conversations

                # Intenta obtener una respuesta del chatbot
                chat_completion = client.chat.completions.create(messages=messages, model="llama3-8b-8192")
                response = chat_completion.choices[0].message.content

                # Agregar la respuesta del chatbot al historial de conversaciones
                conversations.append({"role": "assistant", "content": response})

                # Guardar las conversaciones actualizadas en el archivo JSON
                save_conversations(conversations)

            except Exception as e:
                print(f"Error al obtener la respuesta del chatbot: {e}")
                response = "Hubo un error al procesar tu mensaje. Por favor, intenta de nuevo."

        return jsonify({"response": response}), 200

    # GET request handling
    conversations = load_conversations()
    return render_template('index.html', conversations=conversations, response=None)


if __name__ == '__main__':
    # Ejecutar la aplicación Flask en modo de depuración
    app.run(debug=True)
