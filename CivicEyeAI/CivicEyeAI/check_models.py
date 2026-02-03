import google.generativeai as genai
import os
from dotenv import load_dotenv

# ---------------------------------------------------------
# FIX: No path argument. This searches current & parent folders automatically.
load_dotenv() 
# ---------------------------------------------------------

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print(f"❌ Error: API Key still not found.")
    print(f"   Current Folder: {os.getcwd()}")
    print("   Make sure a file named '.env' exists in this folder or above.")
else:
    print(f"✅ Success! Key found: {api_key[:10]}...")
    genai.configure(api_key=api_key)
    
    print("\n🔍 Checking available models...")
    try:
        found_any = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"   • {m.name}")
                found_any = True
        
        if not found_any:
            print("   ⚠️ No models found. Your key might be new/limited.")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")