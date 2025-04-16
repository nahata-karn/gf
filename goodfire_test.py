import goodfire
import traceback

# Your API key
API_KEY = "sk-goodfire-IqKhz6CY6s-Z_pCrBE4zYljsY_PGOMHkxL3fpZ-lC5Z-U4VgfL-WGQ"

try:
    print("Testing Goodfire API...")
    
    # Initialize client
    client = goodfire.Client(api_key=API_KEY)
    
    # Create a variant with a smaller model - using the correct model name
    variant = goodfire.Variant("meta-llama/Meta-Llama-3.1-8B-Instruct")
    
    # Question and pre-written response
    question = "What is the essence of life?"
    response = """The essence of life is a profound philosophical question that has been pondered throughout human history. At its core, many philosophers and thinkers suggest that meaning, connection, growth, and experience form the fundamental essence of life."""
    
    # Analyze features
    print(f"Analyzing features for question: '{question}'")
    inspector = client.features.inspect(
        [
            {"role": "user", "content": question},
            {"role": "assistant", "content": response}
        ],
        model=variant
    )
    
    # Display results
    print("\nTop 5 activated features:")
    for activation in inspector.top(k=5):
        print(f"{activation.feature.label}: {activation.activation:.4f}")
    
    print("\nSuccess! Feature analysis complete.")
    
except Exception as e:
    print(f"\nERROR: {str(e)}")
    traceback.print_exc()
    print("\nTroubleshooting:")
    print("- Check API key validity")
    print("- Check internet connection")
    print("- Verify model availability") 