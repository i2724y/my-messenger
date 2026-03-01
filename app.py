import os
from flask import Flask, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# ====== SUPABASE CONFIG ======
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ====== TEST ROUTE ======
@app.route("/")
def home():
    return {"status": "Supabase connected"}

# ====== REGISTER USER ======
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    try:
        response = supabase.table("users").insert({
            "email": email,
            "password": password
        }).execute()

        return jsonify({
            "status": "user created",
            "data": response.data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
