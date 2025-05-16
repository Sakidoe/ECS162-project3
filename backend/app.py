from flask import Flask, jsonify, send_from_directory, request
import os
import requests
from flask_cors import CORS

static_path = os.getenv('STATIC_PATH', 'static')
template_path = os.getenv('TEMPLATE_PATH', 'templates')

app = Flask(__name__, static_folder=static_path, template_folder=template_path)
CORS(app)

# NYT API routes
@app.route('/api/key')
def get_key():
#returning api key for frontend
    return jsonify({'apiKey': os.getenv('NYT_API_KEY')})

@app.route('/api/news')
def get_news():

    nyt_api_key = os.getenv('NYT_API_KEY')
    if not nyt_api_key:
        return jsonify({'error': 'API key missing'}), 500

    # Example: Top Stories with Sacramento/Davis keywords
    params = {
        'q': '("Sacramento" OR "Davis" OR "Yolo County")',  # location fixing
        'api-key': nyt_api_key,
        'sort': 'newest',            # want newest
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

@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path=''):
    if path != '' and os.path.exists(os.path.join(static_path, path)):
        return send_from_directory(static_path, path)
    return send_from_directory(template_path, 'index.html')

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=debug_mode)