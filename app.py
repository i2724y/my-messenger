from flask import Flask
import os
from supabase import create_client, Client

app = Flask(__name__)

# Подключение к Supabase через переменные окружения
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def home():
    return {"message": "Server is running"}

# Тестовый роут для проверки подключения
@app.route("/test-db")
def test_db():
    try:
        return {"status": "Supabase connected"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
