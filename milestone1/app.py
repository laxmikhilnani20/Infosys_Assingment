"""from flask import Flask, render_template, request, jsonify
from scraper import WebScraperChatbot
import os

app = Flask(__name__)
# Ensure templates directory is properly located
app.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Initialize chatbot
chatbot = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/initialize', methods=['GET'])
def initialize():
    global chatbot
    try:
        chatbot = WebScraperChatbot()
        return jsonify({'status': 'success', 'message': 'Chatbot initialized successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/scrape', methods=['POST'])
def scrape():
    global chatbot
    if chatbot is None:
        chatbot = WebScraperChatbot()
    
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'status': 'error', 'message': 'URL is required'}), 400
    
    try:
        content = chatbot.scrape_website(url)
        if content.status:
            return jsonify({
                'status': 'success',
                'title': content.title,
                'message': 'Website scraped successfully!'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': content.error
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/ask', methods=['POST'])
def ask():
    global chatbot
    if chatbot is None:
        return jsonify({
            'status': 'error',
            'message': 'Chatbot not initialized. Please refresh the page.'
        }), 400
    
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        return jsonify({'status': 'error', 'message': 'Question is required'}), 400
    
    if not chatbot.scraped_content:
        return jsonify({
            'status': 'error',
            'message': 'Please scrape a website first'
        }), 400
    
    try:
        answer = chatbot.answer_question(question)
        return jsonify({
            'status': 'success',
            'answer': answer
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)"""
from flask import Flask, render_template, request, jsonify
from scraper import WebScraperChatbot
import os

app = Flask(__name__)
# Ensure templates directory is properly located
app.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Initialize chatbot
chatbot = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/initialize', methods=['GET'])
def initialize():
    global chatbot
    try:
        chatbot = WebScraperChatbot()
        return jsonify({'status': 'success', 'message': 'Chatbot initialized successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/scrape', methods=['POST'])
def scrape():
    global chatbot
    if chatbot is None:
        chatbot = WebScraperChatbot()
    
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'status': 'error', 'message': 'URL is required'}), 400
    
    try:
        content = chatbot.scrape_website(url)
        print(f"Scraped content: {content}")  # Debugging statement
        if content.status:
            return jsonify({
                'status': 'success',
                'title': content.title,
                'message': 'Website scraped successfully!'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': content.error
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ...existing code...
@app.route('/ask', methods=['POST'])
def ask():
    global chatbot
    if chatbot is None:
        return jsonify({
            'status': 'error',
            'message': 'Chatbot not initialized. Please refresh the page.'
        }), 400
    
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        return jsonify({'status': 'error', 'message': 'Question is required'}), 400
    
    if not chatbot.scraped_content or not chatbot.scraped_content.status:
        return jsonify({
            'status': 'error',
            'message': 'Please scrape a website first'
        }), 400
    
    try:
        print(f"Scraped content before answering: {chatbot.scraped_content}")  # Debugging statement
        answer = chatbot.answer_question(question)
        return jsonify({
            'status': 'success',
            'answer': answer
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
# ...existing code...
if __name__ == '__main__':
    app.run(debug=True, port=5000)