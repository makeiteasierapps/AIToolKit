from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from site_builder import page_builder_pipeline

app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": "http://localhost:5000",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})
@app.route('/')
def index():
    tools = [
        {'name': 'Website Builder', 'url': 'site_builder'},
        {'name': 'AgentSearch', 'url': 'agent_search'},
    ]
    
    return render_template('index.html', tools=tools)

# Site Builder routes
@app.route('/site_builder')
def site_builder():
    return render_template('site_builder.html')

@app.route('/page_builder', methods=['POST'])
def start_pipeline():
    try:
        data = request.get_json()
        if not data or 'website-description' not in data:
            return Response(
                'data: {"type": "error", "message": "Missing website description"}\n\n',
                mimetype='text/event-stream'
            )
            
        description = data.get('website-description')
        if not description.strip():
            return Response(
                'data: {"type": "error", "message": "Website description cannot be empty"}\n\n',
                mimetype='text/event-stream'
            )
        
        def generate():
            try:
                for html_update in page_builder_pipeline(description):
                    yield f"data: {html_update}\n\n"
            except Exception as e:
                yield f'data: {{"type": "error", "message": "Pipeline error: {str(e)}"}}\n\n'
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream'
        )
        
    except Exception as e:
        return Response(
            f'data: {{"type": "error", "message": "Server error: {str(e)}"}}\n\n',
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
