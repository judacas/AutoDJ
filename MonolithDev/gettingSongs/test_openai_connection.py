#!/usr/bin/env python3
"""
Test script to verify OpenAI API connection using the project's config.

This script tests if the OpenAI API key is properly configured and if we can
make a simple request to the OpenAI API.
"""

import sys
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    print("[ERROR] OpenAI package not installed. Please run: pip install openai")
    sys.exit(1)

from config import get_openai_api_key


def test_openai_connection() -> bool:
    """
    Test OpenAI API connection with a simple math question.

    Returns:
        bool: True if connection successful, False otherwise
    """
    print("[TEST] Testing OpenAI API connection...")

    # Get API key from config
    api_key: Optional[str] = get_openai_api_key()

    if not api_key:
        print("[ERROR] OPENAI_API_KEY not found in environment variables.")
        print("        Please set OPENAI_API_KEY in your .env file.")
        return False

    if api_key == "":
        print("[ERROR] OPENAI_API_KEY is empty.")
        return False

    print(f"[OK] API key found (length: {len(api_key)} characters)")

    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)

        # Make a simple test request
        print("[TEST] Making test request to OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "What is 1 + 2? Please respond with just the number.",
                }
            ],
            max_tokens=10,
            temperature=0,
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
        return False


def main():
    """Main function to run the OpenAI connection test."""
    print("AutoDJ OpenAI Connection Test")
    print("=" * 40)

    success = test_openai_connection()

    print("=" * 40)
    if success:
        print("[PASS] All tests passed! OpenAI integration is ready.")
        sys.exit(0)
    else:
        print("[FAIL] Test failed. Please check your OpenAI API configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()
