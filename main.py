from flask import Flask, render_template, request
import os
from config import(
    HOST,
    PORT
)
from view import (
    stream_brochure
    )
    
# )
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_brochure', methods=['POST'])
def generate_brochure():
    company_name = request.form.get('company_name')
    company_url = request.form.get('company_url')
    # Placeholder for AI-generated content
    # result = stream_brochure(company_name, company_url)
    
    return stream_brochure(company_name, company_url)  # Return streaming response

if __name__ == '__main__':
    app.run(debug=True,host=HOST ,port=PORT)