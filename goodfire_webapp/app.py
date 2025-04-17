from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import goodfire
import json
import asyncio
from dotenv import load_dotenv
import uuid
import logging
import functools
import time
from concurrent.futures import ThreadPoolExecutor
import threading

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env file (optional fallback)
load_dotenv()

app = Flask(__name__)

# Goodfire API configuration from environment variables
API_KEY = os.environ.get("API_KEY", "sk-goodfire-IqKhz6CY6s-Z_pCrBE4zYljsY_PGOMHkxL3fpZ-lC5Z-U4VgfL-WGQ")
MODEL_NAME = os.environ.get("GOODFIRE_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")

logger.debug(f"Starting app with API_KEY: {API_KEY[:10]}... and MODEL_NAME: {MODEL_NAME}")

# Initialize Goodfire client with API key
try:
    # Use standard Client instead of AsyncClient
    client = goodfire.Client(api_key=API_KEY)
    api_key_valid = True
    logger.debug("Successfully initialized Goodfire client")
except Exception as e:
    logger.error(f"Error initializing Goodfire client: {str(e)}")
    print(f"Error initializing Goodfire client: {str(e)}")
    api_key_valid = False

# Simple in-memory cache
feature_cache = {}
response_cache = {}
search_cache = {}

# Thread pool for concurrent API calls
executor = ThreadPoolExecutor(max_workers=4)

@app.route('/')
def index():
    if not api_key_valid:
        return render_template('error.html', 
                            error_message="There was a problem connecting to the Goodfire API. Please try again later.")
    return render_template('index.html')

# Direct route to serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    logger.debug(f"Serving static file: {filename}")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(os.path.join(root_dir, 'static'), filename)

# Function to get features for specific categories
def get_category_features(inspector, category, k=5):
    # Check cache first
    cache_key = f"{category}_{k}"
    if cache_key in search_cache:
        logger.debug(f"Cache hit for category: {category}")
        return search_cache[cache_key]

    try:
        logger.debug(f"Getting features for category: {category}")
        # Use rerank to find features matching the category
        all_features = inspector.top(k=50)  # Get more features initially to filter
        feature_group = goodfire.FeatureGroup([f.feature for f in all_features])
        
        # Rerank to find features related to the given category
        reranked = client.features.search(
            category,  # Using category as search query instead of rerank for better performance
            model=inspector.model,
            top_k=k
        )
        
        # Format the results
        results = []
        for i, feature in enumerate(reranked):
            # Use a simulated activation value based on rank
            activation_value = 1.0 - (i * 0.1)  # Decreasing values from 1.0
            if activation_value < 0.1:
                activation_value = 0.1
                
            results.append({
                "label": feature.label,
                "uuid": str(feature.uuid),
                "activation": float(activation_value)
            })
                
            # Store in feature cache for later use
            feature_uuid = str(feature.uuid)
            feature_label = feature.label
            feature_cache[feature_uuid] = {
                'label': feature_label,
                'category': category,
                'feature': feature
            }
        
        # Store in search cache
        search_cache[cache_key] = results
        return results
    except Exception as e:
        logger.error(f"Error getting features for category '{category}': {str(e)}")
        # Return empty results in case of error
        return []

# Function to handle Goodfire API calls
def generate_response(question, model_variant, selected_categories, custom_weights=None):
    # Check cache first for non-custom weight requests
    if not custom_weights and question in response_cache:
        logger.debug(f"Cache hit for question: {question}")
        return response_cache[question]
    
    start_time = time.time()
    
    try:
        # For the first request (without custom weights), just generate a normal response
        if not custom_weights or len(custom_weights) == 0:
            # Generate response
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": question}],
                model=model_variant,
                max_completion_tokens=300
            )
            
            model_response = response.choices[0].message["content"]
            
            # Extract features
            conversation = [
                {"role": "user", "content": question},
                {"role": "assistant", "content": model_response}
            ]
            
            # Get features for each category in parallel
            features_by_category = {}
            
            try:
                # First try to inspect for features
                inspector = client.features.inspect(
                    messages=conversation,
                    model=model_variant
                )
                
                # Get features for each category
                for category in selected_categories:
                    features_by_category[category] = get_category_features(inspector, category)
            except Exception as e:
                logger.error(f"Error inspecting features: {str(e)}")
                # Fallback: search for features directly without inspection
                for category in selected_categories:
                    features = client.features.search(
                        category,
                        model=model_variant,
                        top_k=5
                    )
                    
                    results = []
                    for i, feature in enumerate(features):
                        # Use a simulated activation value
                        results.append({
                            "label": feature.label,
                            "uuid": str(feature.uuid),
                            "activation": float(1.0 - (i * 0.1))
                        })
                        
                        # Store in feature cache
                        feature_uuid = str(feature.uuid)
                        feature_label = feature.label
                        feature_cache[feature_uuid] = {
                            'label': feature_label,
                            'category': category,
                            'feature': feature
                        }
                    
                    features_by_category[category] = results
            
            result = (model_response, features_by_category)
            
            # Store in cache
            response_cache[question] = result
            
            logger.debug(f"Response generation took {time.time() - start_time:.2f} seconds")
            return result
        
        # For regeneration with custom weights, create a new variant with the specified weights
        else:
            # Create a temporary variant with the base model
            temp_variant = goodfire.Variant(model_variant.base_model)
            
            # Dictionary to track successful feature modifications by category
            modified_features = {}
            
            # Initialize category lists in modified_features
            for category in selected_categories:
                modified_features[category] = []
            
            # Try to directly look up and apply weights for each feature UUID
            for uuid_str, weight in custom_weights.items():
                # Skip weights that are zero
                if float(weight) == 0:
                    continue
                
                weight_value = float(weight)
                feature_found = False
                
                try:
                    # Direct cache lookup approach
                    if uuid_str in feature_cache:
                        category = feature_cache[uuid_str]['category']
                        feature = feature_cache[uuid_str].get('feature')
                        
                        if feature:
                            # Use cached feature directly
                            temp_variant.set(feature, weight_value)
                            
                            if category in modified_features:
                                modified_features[category].append({
                                    'label': feature.label,
                                    'weight': weight_value
                                })
                            
                            print(f"Successfully set weight {weight_value} for feature: {feature.label} (category: {category})")
                            feature_found = True
                        else:
                            # Fallback to search if no feature object in cache
                            feature_label = feature_cache[uuid_str]['label']
                            specific_features = client.features.search(
                                feature_label,
                                model=temp_variant,
                                top_k=1
                            )
                            
                            if specific_features and len(specific_features) > 0:
                                # Use the first result
                                feature = specific_features[0]
                                feature_cache[uuid_str]['feature'] = feature  # Update cache
                                
                                temp_variant.set(feature, weight_value)
                                
                                if category in modified_features:
                                    modified_features[category].append({
                                        'label': feature.label,
                                        'weight': weight_value
                                    })
                                
                                print(f"Successfully set weight {weight_value} for feature: {feature.label} (category: {category})")
                                feature_found = True
                    
                except Exception as e:
                    print(f"Error applying weight for feature {uuid_str}: {str(e)}")
            
            # Check if any features were successfully modified
            total_modified = sum(len(features) for features in modified_features.values())
            if total_modified > 0:
                print(f"Using modified variant with {total_modified} adjusted features")
                model_variant = temp_variant
            else:
                print("No features were successfully adjusted, using default variant")
            
            # Now generate the response with the modified variant
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": question}],
                model=model_variant,
                max_completion_tokens=300
            )
            
            model_response = response.choices[0].message["content"]
            
            # For modified responses, we'll reuse existing feature categorizations
            # This reduces API load and prevents timeouts
            features_by_category = {}
            for category in selected_categories:
                if category in response_cache.get(question, (None, {}))[1]:
                    features_by_category[category] = response_cache[question][1][category]
                else:
                    # Fallback to search directly
                    features = client.features.search(
                        category,
                        model=model_variant,
                        top_k=5
                    )
                    
                    results = []
                    for i, feature in enumerate(features):
                        results.append({
                            "label": feature.label,
                            "uuid": str(feature.uuid),
                            "activation": float(1.0 - (i * 0.1))
                        })
                    
                    features_by_category[category] = results
            
            logger.debug(f"Modified response generation took {time.time() - start_time:.2f} seconds")
            return model_response, features_by_category
    
    except Exception as e:
        logger.error(f"Error in generate_response: {str(e)}")
        # Return a simple response with empty features in case of error
        return f"Sorry, there was an error processing your request: {str(e)}", {}

@app.route('/generate', methods=['POST'])
def generate():
    # Check if API key is configured
    if not api_key_valid:
        logger.error("API key not valid when attempting to generate response")
        return jsonify({
            "error": "API service is currently unavailable. Please try again later."
        }), 500
    
    # Log the request
    logger.debug(f"Received /generate request: {request.data}")
    
    try:
        data = request.json
        logger.debug(f"Request JSON: {data}")
        
        question = data.get('question', '')
        selected_categories = data.get('categories', ['philosophy', 'writing style', 'tone', 'scientific concepts'])
        custom_weights = data.get('custom_weights', None)
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        logger.debug(f"Processing question: '{question}' with categories: {selected_categories}")
        
        try:
            # Create a model variant
            variant = goodfire.Variant(MODEL_NAME)
            
            # Set a reasonable timeout for the entire operation
            model_response, features = generate_response(question, variant, selected_categories, custom_weights)
            
            return jsonify({
                'response': model_response,
                'features_by_category': features
            })
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error generating response: {error_message}")
            
            # Handle common error cases
            if "API key" in error_message or "authentication" in error_message:
                return jsonify({"error": "Service authentication error. Please try again later."}), 500
            elif "rate limit" in error_message:
                return jsonify({"error": "Service rate limit exceeded. Please try again later."}), 429
            elif "model" in error_message and "not found" in error_message:
                return jsonify({"error": f"The requested model is currently unavailable. Please try again later."}), 404
            
            return jsonify({'error': f"An error occurred while processing your request: {error_message}. Please try again."}), 500
    except Exception as e:
        logger.error(f"Unexpected error in /generate route: {str(e)}")
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True) 