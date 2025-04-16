import goodfire
import os
import sys

# Use the API key from app.py or environment
API_KEY = os.environ.get("API_KEY", "sk-goodfire-IqKhz6CY6s-Z_pCrBE4zYljsY_PGOMHkxL3fpZ-lC5Z-U4VgfL-WGQ")
MODEL_NAME = "meta-llama/Meta-Llama-3.1-8B-Instruct"

print(f"Goodfire version: {goodfire.__version__}")
print(f"Using API key: {API_KEY[:10]}...")
print(f"Using model: {MODEL_NAME}")

try:
    print("\n1. Initializing client...")
    client = goodfire.Client(api_key=API_KEY)
    print("Client initialized successfully")
    
    print("\n2. Creating variant...")
    variant = goodfire.Variant(MODEL_NAME)
    print(f"Variant created successfully: {variant}")
    
    print("\n3. Testing chat completion...")
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello, world!"}],
        model=variant,
        max_completion_tokens=10
    )
    print(f"Chat completion successful. Response: {response.choices[0].message['content']}")
    
    print("\n4. Testing feature inspection...")
    conversation = [
        {"role": "user", "content": "Hello, world!"},
        {"role": "assistant", "content": "Hello! How can I assist you today?"}
    ]
    
    try:
        inspector = client.features.inspect(
            messages=conversation,
            model=variant
        )
        print("Feature inspection successful!")
        print(f"Top features: {[f.feature.label for f in inspector.top(k=3)]}")
    except Exception as e:
        print(f"Feature inspection failed: {str(e)}")
    
    print("\n5. Testing feature search...")
    try:
        features = client.features.search(
            "friendly tone",
            model=variant,
            top_k=3
        )
        print("Feature search successful!")
        print(f"Features found: {[f.label for f in features]}")
    except Exception as e:
        print(f"Feature search failed: {str(e)}")
    
except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1)

print("\nTest completed!") 