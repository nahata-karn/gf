import goodfire
import traceback

# Your API key
API_KEY = "sk-goodfire-IqKhz6CY6s-Z_pCrBE4zYljsY_PGOMHkxL3fpZ-lC5Z-U4VgfL-WGQ"

try:
    print("Testing Goodfire Feature Steering...")
    
    # Initialize client
    client = goodfire.Client(api_key=API_KEY)
    
    # Create a variant with correct model name
    variant = goodfire.Variant("meta-llama/Meta-Llama-3.1-8B-Instruct")
    
    # Question
    question = "What is the essence of life?"
    
    # Method 1: Using feature search and manual weights
    print("\n--- Method 1: Manual Feature Adjustment ---")
    
    # Search for philosophical features
    print("Searching for philosophical features...")
    philosophical_features = client.features.search(
        "philosophical deep thinking",
        model=variant,
        top_k=3
    )
    
    # Print found features
    print("\nFound philosophical features:")
    for feature in philosophical_features:
        print(f"- {feature.label}")
    
    # Modify the variant to amplify philosophical features
    print("\nAmplifying philosophical features...")
    for feature in philosophical_features:
        variant.set(feature, 0.7)  # Boost philosophical features
    
    # Generate response with modified features
    print("\nGenerating response with amplified philosophical features...")
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": question}],
        model=variant,
        max_completion_tokens=150
    )
    
    print("\nResponse with amplified philosophical features:")
    print(response.choices[0].message["content"])
    
    # Reset the variant
    variant.reset()
    
    # Method 2: Using AutoSteer
    print("\n\n--- Method 2: Using AutoSteer ---")
    print("Using AutoSteer to automatically adjust features...")
    
    # Use AutoSteer to automatically find and adjust features
    edits = client.features.AutoSteer(
        specification="deeply poetic and metaphorical",
        model=variant
    )
    
    # Apply the edits
    variant.set(edits)
    
    # Generate response with auto-steered features
    print("\nGenerating response with auto-steered features...")
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": question}],
        model=variant,
        max_completion_tokens=150
    )
    
    print("\nResponse with auto-steered poetic features:")
    print(response.choices[0].message["content"])
    
    print("\nFeature steering completed successfully.")
    
except Exception as e:
    print(f"\nERROR: {str(e)}")
    traceback.print_exc()
    print("\nTroubleshooting:")
    print("- Check API key validity")
    print("- Check internet connection") 
    print("- Verify model availability") 