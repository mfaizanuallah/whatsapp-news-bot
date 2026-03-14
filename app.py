import os, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# CONFIG - We are hardcoding these for now to ensure it works. 
# Once the bot is live, we can move them back to Render variables correctly.
ACCESS_TOKEN = "EAF0NF779rTMBQxjgVnXzUjFnWuRDVuzUw0TkbZBmYxP7NcqTMlvl0CDa7vPnAoREg7cILZAIxG31ZCPeWOrOhtR3jJ0i7WB3C1pCbclb6AGUIfZCpvp2ebNw8JBBO1zzlEP7ixM3hr7ZCEsZCSqmDLFNKsZAcbQjYeZCCjwyBfg8StjzZB0jpQbGcybXkfNtCF6Yb0mWAnPBKqW7OtxItR9txRcQfn87oPsxeLIppMvZCRodfnWKZACp5yVpJkqahdy1WTrw6XqVAm5BNUCncZAnCAJPsdyotPPYBUBZCWZB8ZD"
PHONE_ID = "1050947264767706"
VERIFY_TOKEN = "mongol_secret_123"
NEWS_API_KEY = "pub_5e617ce165b44f04ad98f9c1c1bffddd"

def get_pakistan_news():
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&country=pk&language=en"
    try:
        r = requests.get(url).json()
        articles = r.get('results', [])[:3]
        if not articles:
            return "No news found at the moment."
        return "\n\n".join([f"*{a['title']}*\n{a['link']}" for a in articles])
    except Exception as e:
        print(f"News Error: {e}")
        return "Could not fetch news right now. Try again later."

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # 1. Handle Meta's Verification (GET)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Verification failed", 403

    # 2. Handle Incoming Messages (POST)
    data = request.get_json()
    print(f"Incoming Data: {data}") # This will show up in your Render Logs

    try:
        if data.get("entry") and data["entry"][0].get("changes"):
            value = data["entry"][0]["changes"][0]["value"]
            if value.get("messages"):
                message = value["messages"][0]
                sender = message["from"]
                text = message.get("text", {}).get("body", "").strip()

                if text == ".":
                    news = get_pakistan_news()
                    # Send WhatsApp reply
                    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
                    headers = {
                        "Authorization": f"Bearer {ACCESS_TOKEN}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": sender,
                        "type": "text",
                        "text": {"body": news}
                    }
                    response = requests.post(url, json=payload, headers=headers)
                    print(f"WhatsApp API Response: {response.json()}")

    except Exception as e:
        print(f"Error processing message: {e}")

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
