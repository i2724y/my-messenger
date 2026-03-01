import os
import bcrypt
import jwt
import datetime
from flask import Flask, request, jsonify
from supabase import create_client, Client
from functools import wraps

app = Flask(__name__)

# ==============================
# CONFIG
# ==============================

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
JWT_SECRET = os.environ.get("JWT_SECRET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==============================
# HELPER: TOKEN REQUIRED
# ==============================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user_id = data["user_id"]
        except Exception:
            return jsonify({"error": "Invalid token"}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated

# ==============================
# TEST ROUTE
# ==============================

@app.route("/")
def home():
    return {"status": "API working"}

# ==============================
# REGISTER
# ==============================

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    # Проверка существования пользователя
    existing = supabase.table("users").select("*").eq("email", email).execute()
    if existing.data:
        return jsonify({"error": "User already exists"}), 400

    # Хешируем пароль
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    hashed_password = hashed_password.decode("utf-8")

    # Сохраняем
    response = supabase.table("users").insert({
        "email": email,
        "password": hashed_password
    }).execute()

    user_id = response.data[0]["id"]

    # Создаём токен
    token = jwt.encode({
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, JWT_SECRET, algorithm="HS256")

    return jsonify({
        "status": "user created",
        "token": token
    })

# ==============================
# LOGIN
# ==============================

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = supabase.table("users").select("*").eq("email", email).execute()

    if not user.data:
        return jsonify({"error": "User not found"}), 404

    user = user.data[0]
    stored_password = user["password"].encode("utf-8")

    # Проверяем пароль
    if not bcrypt.checkpw(password.encode("utf-8"), stored_password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Генерируем токен
    token = jwt.encode({
        "user_id": user["id"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, JWT_SECRET, algorithm="HS256")

    return jsonify({
        "status": "login successful",
        "token": token
    })

# ==============================
# PROTECTED ROUTE
# ==============================

@app.route("/profile", methods=["GET"])
@token_required
def profile(current_user_id):
    user = supabase.table("users").select("id, email, created_at").eq("id", current_user_id).execute()

    return jsonify(user.data[0])

# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
