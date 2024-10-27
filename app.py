from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from json_parser import get_parsed_data
from site_builder import promptify

app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": "http://127.0.0.1:5500",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})
@app.route('/')
def index():
    tools = [
        {'name': 'JSON Parser', 'url': 'json_parser'},
        {'name': 'Website Builder', 'url': 'site_builder'},
        {'name': 'AgentSearch', 'url': 'agent_search'},
    ]
    
    return render_template('index.html', tools=tools)
# Json Parser routes
@app.route('/json_parser')
def json_parser():
    return render_template('json_parser.html')

# Site Builder routes
@app.route('/site_builder')
def site_builder():
    return render_template('site_builder.html')

@app.route('/run_parser_code', methods=['POST'])
def run_parser_code():
    json_data = request.form.get('json_data') #This receives the data sent from the form
    parsed_data = get_parsed_data(json_data)
    return parsed_data

@app.route('/run_site_prompting', methods=['POST'])
def run_site_prompting():
    data = request.get_json()
    description = data.get('website-description')
    
    def generate():
        for html_update in promptify(description):
            yield f"data: {html_update}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream'
    )

# Agent Search
@app.route('/agent_search')
def agent_search():
    return render_template('agent_search.html')

@app.route('/submit_brand', methods=['POST'])
def submit_brand():
    data = request.get_json()
    brand = data.get('brand', '')
    if brand:
        response = f"Received brand: {brand}"
    else:
        response = "No brand received"
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
