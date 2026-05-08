"""Quick test script to verify Gemini migration.

Run this after setting GEMINI_API_KEY in your .env file:
    python backend/test_gemini_migration.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.llm import get_llm_service


async def test_gemini_service():
    """Test that Gemini service is configured and working."""
    
    print("=" * 60)
    print("VendorAuditAI - Gemini Migration Test")
    print("=" * 60)
    
    # Get the LLM service
    llm_service = get_llm_service()
    
    print(f"\n✅ LLM Service Type: {type(llm_service).__name__}")
    print(f"✅ Model: {llm_service.model}")
    print(f"✅ Is Configured: {llm_service.is_configured}")
    
    if not llm_service.is_configured:
        print("\n❌ ERROR: Gemini service not configured!")
        print("Please set GEMINI_API_KEY in your .env file")
        print("Get a free key at: https://aistudio.google.com/apikey")
        return False
    
    # Test a simple query
    print("\n" + "=" * 60)
    print("Testing Simple Query...")
    print("=" * 60)
    
    test_chunks = [
        {
            "content": "The vendor implements multi-factor authentication for all user accounts.",
            "section_header": "Access Control",
            "page_number": 5,
        }
    ]
    
    try:
        result = await llm_service.analyze_document(
            chunks=test_chunks,
            framework="soc2_tsc",
            document_type="soc2",
            max_tokens=500,
        )
        
        print(f"\n✅ Analysis successful!")
        print(f"   Model used: {result.model}")
        print(f"   Input tokens: {result.input_tokens}")
        print(f"   Output tokens: {result.output_tokens}")
        print(f"   Findings count: {len(result.findings)}")
        print(f"   Summary: {result.summary[:100]}...")
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION SUCCESSFUL!")
        print("=" * 60)
        print("\nGemini 1.5 Flash is working correctly.")
        print("You can now use VendorAuditAI with Google Gemini!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPlease check:")
        print("1. GEMINI_API_KEY is set in .env")
        print("2. API key is valid")
        print("3. google-generativeai package is installed")
        return False


def main():
    """Run the test."""
    # Check for API key
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "your_google_gemini_api_key_here":
        print("\n❌ ERROR: GEMINI_API_KEY not configured!")
        print("\nSteps to fix:")
        print("1. Get a free API key: https://aistudio.google.com/apikey")
        print("2. Copy .env.example to .env")
        print("3. Set GEMINI_API_KEY=your_actual_key in .env")
        print("4. Run this test again")
        sys.exit(1)
    
    # Run the async test
    success = asyncio.run(test_gemini_service())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
