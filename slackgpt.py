import os
import openai
from slack_bolt import App, Say
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import logging
import asyncio
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

load_dotenv()

SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Initialize the Slack app
app = App()

async def chat_with_gpt(prompt):
    openai.api_key = OPENAI_API_KEY
    response = await asyncio.to_thread(
        openai.ChatCompletion.create,
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

    await say(f'holaaaa')

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
    event = body['event']
    if event.get('channel_type') == 'im':
        text = event['text']
        user = event['user']

        await say(f'holaaaa')
        print("Initial message sent")  # Added this line

        if f'<@{slack_bot_user_id}>' in text:
            try:
                # Remove the mention itself from the text and strip leading/trailing whitespaces
                cleaned_text = text.replace(f'<@{slack_bot_user_id}>', '').strip()

                # Get a response from GPT
                print(f"Cleaned text: {cleaned_text}")
                gpt_response = await chat_with_gpt(cleaned_text)
                print(f"GPT response: {gpt_response}")

                # Send the response to the user
                print(f"User: {user}")
                print(f"Response: {gpt_response}")
                await say(f'<@{user}> {gpt_response}')

            except Exception as e:
                print(f"Error responding to message: {e}")
        else:
            print("Bot not mentioned in the message")  # Added this line
    else:
        print("Not an IM event")  # Added this line


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
        logging.info("Getting response from GPT-3")
        assistant_reply = await chat_with_gpt(text)
        logging.info(f"Assistant reply: {assistant_reply}")

        # Respond to the user with the GPT-3 response
        await respond(assistant_reply)
        logging.info("Response sent")

    except Exception as e:
        logging.exception(f"Error handling slash command: {e}")

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
