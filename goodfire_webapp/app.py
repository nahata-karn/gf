from flask import Flask, render_template, request, jsonify
import os
import goodfire
import json
import asyncio
from dotenv import load_dotenv
import uuid

# Load environment variables from .env file (optional fallback)
load_dotenv()

app = Flask(__name__)

# Goodfire API configuration with hardcoded API key
API_KEY = "sk-goodfire-IqKhz6CY6s-Z_pCrBE4zYljsY_PGOMHkxL3fpZ-lC5Z-U4VgfL-WGQ"
MODEL_NAME = os.environ.get("GOODFIRE_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")

# Initialize Goodfire client with hardcoded API key
try:
    # Use AsyncClient instead of Client for async operations
    client = goodfire.AsyncClient(api_key=API_KEY)
    api_key_valid = True
except Exception as e:
    print(f"Error initializing Goodfire client: {str(e)}")
    api_key_valid = False

@app.route('/')
def index():
    if not api_key_valid:
        return render_template('error.html', 
                            error_message="There was a problem connecting to the Goodfire API. Please try again later.")
    return render_template('index.html')

# Helper function to run async tasks
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Async function to get features for specific categories
async def get_category_features(inspector, category, k=5):
    # Use rerank to find features matching the category
    all_features = inspector.top(k=50)  # Get more features initially to filter
    feature_group = goodfire.FeatureGroup([f.feature for f in all_features])
    
    # Rerank to find features related to the given category
    reranked = await client.features.rerank(
        features=feature_group,
        query=category,
        model=inspector.model,
        top_k=k
    )
    
    # Format the results
    results = []
    for feature in reranked:
        # Find the original activation value
        for activation in all_features:
            if activation.feature.uuid == feature.uuid:
                results.append({
                    "label": feature.label,
                    "uuid": str(feature.uuid),
                    "activation": float(activation.activation)
                })
                break
    
    return results

# Store feature cache by label for easier lookup
feature_cache = {}

# Async function to handle Goodfire API calls
async def generate_response(question, model_variant, selected_categories, custom_weights=None):
    # For the first request (without custom weights), just generate a normal response
    if not custom_weights or len(custom_weights) == 0:
        # Generate response
        response = await client.chat.completions.create(
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
        
        # Inspect the response for features
        inspector = await client.features.inspect(
            messages=conversation,
            model=model_variant
        )
        
        # Get features by category
        features_by_category = {}
        for category in selected_categories:
            features_by_category[category] = await get_category_features(inspector, category)
            
            # Store features in cache for later use with feature adjustment
            for feature_data in features_by_category[category]:
                feature_uuid = feature_data['uuid']
                feature_label = feature_data['label']
                feature_cache[feature_uuid] = {
                    'label': feature_label,
                    'category': category
                }
        
        return model_response, features_by_category
    
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
                # The lookup method seems to require a list of indices, not UUIDs
                # Let's skip that approach and go directly to label-based search which is more reliable
                if uuid_str in feature_cache:
                    category = feature_cache[uuid_str]['category']
                    feature_label = feature_cache[uuid_str]['label']
                    
                    # Search specifically for this feature label
                    specific_features = await client.features.search(
                        feature_label,
                        model=temp_variant,
                        top_k=3
                    )
                    
                    if specific_features and len(specific_features) > 0:
                        # Use the first result (most relevant)
                        feature = specific_features[0]
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
        response = await client.chat.completions.create(
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
        
        # Inspect the response for features
        inspector = await client.features.inspect(
            messages=conversation,
            model=model_variant
        )
        
        # Get features by category
        features_by_category = {}
        for category in selected_categories:
            features_by_category[category] = await get_category_features(inspector, category)
        
        return model_response, features_by_category

@app.route('/generate', methods=['POST'])
def generate():
    # Check if API key is configured
    if not api_key_valid:
        return jsonify({
            "error": "API service is currently unavailable. Please try again later."
        }), 500
    
    data = request.json
    question = data.get('question', '')
    selected_categories = data.get('categories', ['philosophy', 'writing style', 'tone', 'scientific concepts'])
    custom_weights = data.get('custom_weights', None)
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    try:
        # Create a model variant
        variant = goodfire.Variant(MODEL_NAME)
        
        # Run async function in sync context
        model_response, features = run_async(generate_response(question, variant, selected_categories, custom_weights))
        
        return jsonify({
            'response': model_response,
            'features_by_category': features
        })
        
    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}")
        
        # Handle common error cases
        if "API key" in error_message or "authentication" in error_message:
            return jsonify({"error": "Service authentication error. Please try again later."}), 500
        elif "rate limit" in error_message:
            return jsonify({"error": "Service rate limit exceeded. Please try again later."}), 429
        elif "model" in error_message and "not found" in error_message:
            return jsonify({"error": f"The requested model is currently unavailable. Please try again later."}), 404
        
        return jsonify({'error': "An error occurred while processing your request. Please try again."}), 500

if __name__ == '__main__':
    app.run(debug=True) 