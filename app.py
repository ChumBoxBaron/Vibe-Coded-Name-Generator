from flask import Flask, render_template, request, jsonify
from baseball_name_generator import BaseballNameGenerator
from census_name_generator import CensusNameGenerator
from generators.funny_generator import FunnyNameGenerator
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Use environment variable in production

# Initialize name generators
try:
    baseball_generator = BaseballNameGenerator()
    census_generator = CensusNameGenerator()
    funny_generator = FunnyNameGenerator()
    logger.info("Name generators initialized successfully")
except Exception as e:
    logger.error(f"Error initializing name generators: {str(e)}")
    raise

@app.route('/')
def index():
    logger.debug("Index route accessed")
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_names():
    data = request.get_json()
    generator_type = data.get('type', 'baseball')
    count = int(data.get('count', 10))
    
    try:
        if generator_type == 'baseball':
            names = baseball_generator.generate_multiple(count)
        elif generator_type == 'unique_census':
            names = census_generator.generate_multiple_unique(count)
        elif generator_type == 'weighted_unique_census':
            names = census_generator.generate_multiple_weighted_unique(count)
        elif generator_type == 'funny':
            names = funny_generator.generate_multiple(count)
        else:
            names = census_generator.generate_multiple(count)
        
        return jsonify({
            'success': True,
            'names': names
        })
    except Exception as e:
        logger.error(f"Error generating names: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    try:
        # Use PORT environment variable for cloud providers 
        port = int(os.environ.get("PORT", 5000))
        debug_mode = os.environ.get("FLASK_ENV", "development") == "development"
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
    except Exception as e:
        logger.error(f"Failed to start Flask server: {str(e)}")
        raise 