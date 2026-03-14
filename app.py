import os, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# CONFIG (From Environment Variables)
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_ID = os.environ.get("PHONE_ID")
VERIFY_TOKEN = "mongol_secret_123" # You will enter this in Meta dashboard

def get_pakistan_news():
    # Using a free news source (Placeholder logic)
    # You can get a free key from newsdata.io
    api_key = os.environ.get("NEWS_API_KEY")
    url = f"https://newsdata.io/api/1/news?apikey={api_key}&country=pk&language=en"
    try:
        r = requests.get(url).json()
        articles = r.get('results', [])[:3]
        return "\n\n".join([f"*{a['title']}*\n{a['link']}" for a in articles])
    except:
        return "Could not fetch news right now. Try again later."

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Meta's verification handshake
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification failed", 403

    # Handle incoming WhatsApp messages
    data = request.get_json()
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        sender = message['from']
        text = message.get('text', {}).get('body', "").strip()

        if text == ".":
            news = get_pakistan_news()
            # Send reply
            url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
            headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
            payload = {"messaging_product": "whatsapp", "to": sender, "type": "text", "text": {"body": news}}
            requests.post(url, json=payload, headers=headers)
    except:
        pass
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
