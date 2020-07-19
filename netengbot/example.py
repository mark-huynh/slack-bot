from slackeventsapi import SlackEventAdapter
from slack import WebClient
import os
import redis
import json

host = "localhost"
port = "6379"
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")

# Create a SlackClient for your bot to use for Web API requests
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_client = WebClient(slack_bot_token)

# Creates a hash in redis to remember the conversation
def add_thread_mem(thread_id, topic):
    r.hmset(thread_id, {"topic": topic, "step": 0})

def get_thread_mem(thread_id):
    return r.hgetall(thread_id)

def increment_step(thread_id):
    temp = get_thread_mem(thread_id)
    temp["step"] += 1
    r.hmset(thread_id, temp)

def is_in_redis(message):
    print(message["thread_ts"])
    # print(get_thread_mem(message["thread_ts"]))
    return message.get("thread_ts") is not None and get_thread_mem(message["thread_ts"]) is not None

# Example responder to greetings
@slack_events_adapter.on("message")
def handle_message(event_data):
    # WRAP SO IT IS NOT FROM THE BOT
    message = event_data["event"]
    # If the incoming message contains "upgrade switch"
    if message.get("subtype") is None and "update switch" in message.get('text'):
        channel = message["channel"]
        text = "Which switch would you like to update?"
        slack_client.chat_postMessage(channel=channel, text=text, thread_ts=message["ts"])
        add_thread_mem(message["ts"], "switch-upgrade")
        return
        # Broken
    if message.get("subtype") is None and is_in_redis(message):
        # print(message)
        channel = message["channel"]
        text = "bar"
        slack_client.chat_postMessage(channel=channel, text=text, thread_ts=message["thread_ts"])
        print(json.dumps(message, indent=2))

    # if message.get("subtype") is None and 


# Example reaction emoji echo
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    event = event_data["event"]
    emoji = event["reaction"]
    channel = event["item"]["channel"]
    text = ":%s:" % emoji
    slack_client.chat_postMessage(channel=channel, text=text)

# Error events
@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))

# Once we have our event listeners configured, we can start the
# Flask server with the default `/events` endpoint on port 3000
slack_events_adapter.start(port=3000)
