#!/usr/bin/env python3
"""
Standalone OpenAI API test script.

This script tests OpenAI API connection without using the project's config system.
It sets up the OpenAI client directly and makes a simple test request.
"""

import os
import sys
from typing import Optional

try:
    from dotenv import load_dotenv
    from openai import OpenAI
except ImportError as e:
    print(f"[ERROR] Missing package: {e}")
    print("Please run: pip install openai python-dotenv")
    sys.exit(1)

# Load environment variables from .env file
load_dotenv()


def test_openai_standalone() -> bool:
    """
    Test OpenAI API connection with direct setup (no config system).
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    print("[TEST] Testing OpenAI API connection (standalone)...")
    
    # Get API key directly from environment
    api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not found in environment variables.")
        print("        Please set OPENAI_API_KEY in your environment or .env file.")
        return False
    
    if api_key == "":
        print("[ERROR] OPENAI_API_KEY is empty.")
        return False
    
    print(f"[OK] API key found (length: {len(api_key)} characters)")
    
    try:
        # Initialize OpenAI client directly
        print("[TEST] Initializing OpenAI client...")
        client = OpenAI(api_key=api_key)
        
        # Make a simple test request
        print("[TEST] Making test request to OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "What is 1 + 2? Please respond with just the number."}
            ],
            max_tokens=10,
            temperature=0
        )
        
        # Extract and display the response
        answer = response.choices[0].message.content.strip()
        print(f"[RESPONSE] OpenAI Response: {answer}")
        
        # Verify the answer
        if answer == "3":
            print("[SUCCESS] Test successful! OpenAI API is working correctly.")
            return True
        else:
            print(f"[WARNING] Unexpected response: {answer} (expected: 3)")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error connecting to OpenAI API: {e}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        return False


def test_with_different_models() -> bool:
    """
    Test OpenAI API with different models to see which ones work.
    
    Returns:
        bool: True if at least one model works, False otherwise
    """
    print("\n[TEST] Testing different OpenAI models...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] No API key available for model testing.")
        return False
    
    models_to_test = [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo-preview"
    ]
    
    client = OpenAI(api_key=api_key)
    working_models = []
    
    for model in models_to_test:
        try:
            print(f"[TEST] Testing model: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": "Say 'hello'"}
                ],
                max_tokens=5,
                temperature=0
            )
            
            answer = response.choices[0].message.content.strip()
            print(f"[OK] Model {model} responded: {answer}")
            working_models.append(model)
            
        except Exception as e:
            print(f"[ERROR] Model {model} failed: {e}")
    
    if working_models:
        print(f"[SUCCESS] Working models: {', '.join(working_models)}")
        return True
    else:
        print("[ERROR] No models are working.")
        return False


def main():
    """Main function to run the standalone OpenAI connection test."""
    print("AutoDJ OpenAI Standalone Connection Test")
    print("=" * 50)
    
    # Test basic connection
    success = test_openai_standalone()
    
    if success:
        # Test different models
        model_success = test_with_different_models()
    else:
        model_success = False
    
    print("=" * 50)
    if success:
        print("[PASS] Basic OpenAI connection test passed!")
        if model_success:
            print("[PASS] Model testing also passed!")
        else:
            print("[WARNING] Basic test passed but model testing failed.")
        sys.exit(0)
    else:
        print("[FAIL] OpenAI connection test failed.")
        print("[INFO] This might be due to:")
        print("       - Missing or invalid OPENAI_API_KEY")
        print("       - Network connectivity issues")
        print("       - OpenAI API service issues")
        print("       - Package version compatibility")
        sys.exit(1)


if __name__ == "__main__":
    main()
