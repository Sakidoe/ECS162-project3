# app.py
from flask import Flask, redirect, url_for, session, jsonify, request
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
import os
import requests
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

oauth = OAuth(app)
oauth.register(
    name=os.getenv('OIDC_CLIENT_NAME'),
    client_id=os.getenv('OIDC_CLIENT_ID'),
    client_secret=os.getenv('OIDC_CLIENT_SECRET'),
    authorization_endpoint="http://localhost:5556/auth",
    token_endpoint="http://dex:5556/token",
    jwks_uri="http://dex:5556/keys",
    userinfo_endpoint="http://dex:5556/userinfo",
    device_authorization_endpoint="http://dex:5556/device/code",
    client_kwargs={'scope': 'openid email profile'}
)

# MongoDB setup
mongo_client = MongoClient("mongodb://root:rootpassword@mongo:27017/?authSource=admin")
db = mongo_client["mydatabase"]
comments_collection = db["comments"]

@app.route('/api/news')
def get_news():
    nyt_api_key = os.getenv('NYT_API_KEY')
    if not nyt_api_key:
        return jsonify({'error': 'API key missing'}), 500
    params = {
        'q': '"Sacramento" OR "Davis" OR "Yolo County"',
        'api-key': nyt_api_key,
        'sort': 'newest',
        'page': request.args.get('page', '1')
    }
    try:
        response = requests.get(
            'https://api.nytimes.com/svc/search/v2/articlesearch.json',
            params=params
        )
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user')
def get_user():
    user = session.get('user')
    if user:
        return jsonify({
            'email': user['email'],
            'role': user.get('name', 'user')
        })
    return jsonify({'error': 'Not logged in'}), 401

@app.route('/api/comments', methods=['GET'])
def get_comments():
    url = request.args.get('url')
    comment_list = list(comments_collection.find({'article_url': url}))
    return jsonify([
        {
            "_id": str(c["_id"]),
            "username": c["username"],
            "content": c["content"],
            "parent_id": str(c["parent_id"]) if c.get("parent_id") else None,
            "role": c.get("role", "user")
        }
        for c in comment_list
    ])

@app.route('/api/comments', methods=['POST'])
def post_comment():
    user = session.get("user")
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    comment = {
        "article_url": data["article_url"],
        "username": user["email"],
        "role": user.get("name", "user"),
        "content": data["content"],
        "timestamp": datetime.utcnow(),
        "parent_id": data.get("parent_id")
    }
    result = comments_collection.insert_one(comment)
    return jsonify({"id": str(result.inserted_id)})


@app.route('/api/comments/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    user = session.get("user")
    if not user or user.get("name") != "moderator": 
        return jsonify({"error": "Forbidden"}), 403
    result = comments_collection.delete_one({"_id": ObjectId(comment_id)})
    return jsonify({"deleted": result.deleted_count}), 200

@app.route('/api/comments/<comment_id>/edit', methods=['PATCH'])
def edit_comment(comment_id):
    user = session.get("user")
    if not user or user.get("name") != "moderator":
        return jsonify({"error": "Forbidden"}), 403

    data = request.json
    new_content = data.get("content", "").strip()
    if not new_content:
        return jsonify({"error": "Content cannot be empty"}), 400

    result = comments_collection.update_one(
        {"_id": ObjectId(comment_id)},
        {"$set": {"content": new_content}}
    )
    return jsonify({"message": "Comment updated"}), 200

@app.route('/')
def home():
    return redirect('http://localhost:5173/')

@app.route('/login')
def login():
    nonce = generate_token()
    session['nonce'] = nonce
    redirect_uri = 'http://localhost:8000/authorize'
    return oauth.flask_app.authorize_redirect(redirect_uri, nonce=nonce)

@app.route('/authorize')
def authorize():
    token = oauth.flask_app.authorize_access_token()
    nonce = session.get('nonce')
    user_info = oauth.flask_app.parse_id_token(token, nonce=nonce)
    session['user'] = user_info
    print(session.get("user"))
    return redirect('http://localhost:5173/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('http://localhost:5173/')



@app.route('/api/debug-session')
def debug_session():
    return jsonify(dict(session))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)