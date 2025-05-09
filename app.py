from flask import Flask, render_template, request, jsonify
from discord_webhook import DiscordWebhook
import sqlite3
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)

# Create the database and table if not exists
def init_db():
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Save message to database
def save_to_database(text):
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (content, timestamp) VALUES (?, ?)', (text, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

# Send to Discord using webhook
def send_to_discord(text):
    webhook = DiscordWebhook(url='YOUR_DISCORD_WEBHOOK_URL', content=text)
    webhook.execute()

# Endpoint 1 - Input Text
@app.route('/input_text', methods=['POST'])
def input_text():
    try:
        data = request.get_json() or request.form  # Support JSON or form
        text = data.get('text')
        if not text:
            return jsonify({"status": "error", "message": "Text is required"}), 400

        # Send to Discord
        send_to_discord(text)

        # Save to database
        save_to_database(text)

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint 3 - Message Retrieval
@app.route('/get_messages', methods=['GET'])
def get_messages():
    try:
        conn = sqlite3.connect('messages.db')
        cursor = conn.cursor()
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)
        cursor.execute('SELECT content, timestamp FROM messages WHERE timestamp >= ?', (cutoff_time.isoformat(),))
        messages = cursor.fetchall()
        conn.close()

        return jsonify({
            "status": "success",
            "messages": [{"text": msg[0], "timestamp": msg[1]} for msg in messages]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Serve HTML Form
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
