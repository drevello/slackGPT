import os
import openai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

load_dotenv()

SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Initialize the Slack app
app = App()

def chat_with_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )

    message = response.choices[0].message["content"].strip()
    return message

@app.event("app_mention")
async def handle_app_mentions(body, say):
    print("App mention event received:", body)
    text = body['event']['text']
    user = body['event']['user']

    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text}
        ]
    )
    assistant_reply = response.choices[0].message.content

    await say(f"<@{user}> {assistant_reply}")

@app.event("message")
async def handle_direct_messages(body, say):
    print("Message event received:", body)
    channel_type = body['event'].get('channel_type')
    
    if channel_type == 'im':
        text = body['event']['text']
        user = body['event']['user']

        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text}
            ]
        )
        assistant_reply = response.choices[0].message.content

        await say(f"<@{user}> {assistant_reply}")

@app.command("/slackgpt")
async def handle_slash_command(ack, respond, command):
    try:
        logging.info("Handling slash command")
        
        # Acknowledge the command request
        await ack()
        logging.info("Command acknowledged")

        # Extract the text from the command
        text = command["text"]

        # Get the response from GPT-3
        assistant_reply = chat_with_gpt(text)

        # Respond to the user with the GPT-3 response
        await respond(assistant_reply)
        logging.info("Response sent")

    except Exception as e:
        logging.exception(f"Error handling slash command: {e}")

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
