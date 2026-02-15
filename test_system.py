#!/usr/bin/env python3
"""
Quick System Test - Verify everything is working
Run this before starting production
"""
import sys
from pathlib import Path

def test_python_version():
    """Test Python version"""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\n📦 Testing dependencies...")
    required = [
        'requests',
        'rapidfuzz',
        'keybert',
        'langdetect',
        'sentence_transformers',
        'pydantic',
        'chromadb',
        'sqlalchemy',
        'aiohttp',
        'dotenv',
        'rich',
        'tenacity',
        'schedule'
    ]
    
    missing = []
    for package in required:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n   ⚠️  Missing packages: {', '.join(missing)}")
        print(f"   Run: pip install {' '.join(missing)}")
        return False
    return True

def test_env_file():
    """Test .env file"""
    print("\n🔑 Testing .env file...")
    env_path = Path('.env')
    
    if not env_path.exists():
        print("   ❌ .env file not found")
        print("   Create it from .env.example:")
        print("   copy .env.example .env")
        return False
    
    # Read and check keys
    content = env_path.read_text()
    
    has_newsapi = 'NEWSAPI_KEY=' in content
    has_gnews = 'GNEWS_API_KEY=' in content
    
    if has_newsapi and has_gnews:
        # Check if keys are filled in
        if 'your_newsapi_key_here' in content or 'your_gnews_key_here' in content:
            print("   ⚠️  .env file exists but keys not configured")
            print("   Edit .env and add your actual API keys")
            return False
        else:
            print("   ✅ .env file configured")
            return True
    else:
        print("   ❌ .env file missing required keys")
        return False

def test_directories():
    """Test required directories"""
    print("\n📁 Testing directories...")
    dirs = ['src', 'src/agents', 'src/memory', 'tests', 'website']
    
    all_exist = True
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ (missing)")
            all_exist = False
    
    return all_exist

def test_source_files():
    """Test critical source files"""
    print("\n📄 Testing source files...")
    files = [
        'src/orchestrator.py',
        'src/config.py',
        'src/agents/base.py',
        'src/agents/collector.py',
        'src/agents/analyzer.py',
        'src/agents/retriever.py',
        'src/agents/writer.py',
        'production_scheduler.py',
        'website/index.html'
    ]
    
    all_exist = True
    for file_name in files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ {file_name} (missing)")
            all_exist = False
    
    return all_exist

def test_imports():
    """Test if main modules can be imported"""
    print("\n🔧 Testing imports...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        
        from src.config import settings
        print("   ✅ src.config")
        
        from src.orchestrator import Orchestrator
        print("   ✅ src.orchestrator")
        
        from src.agents.base import BaseAgent
        print("   ✅ src.agents.base")
        
        from src.agents.collector import CollectorAgent
        print("   ✅ src.agents.collector")
        
        from src.agents.analyzer import AnalyzerAgent
        print("   ✅ src.agents.analyzer")
        
        from src.agents.retriever import RetrieverAgent
        print("   ✅ src.agents.retriever")
        
        from src.agents.writer import WriterAgent
        print("   ✅ src.agents.writer")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 SYSTEM TEST - Verifying Production Readiness")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Python Version", test_python_version()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("Environment File", test_env_file()))
    results.append(("Directories", test_directories()))
    results.append(("Source Files", test_source_files()))
    results.append(("Imports", test_imports()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 60)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\n✅ System is ready for production!")
        print("\nNext steps:")
        print("1. Make sure .env has your API keys")
        print("2. Run: python production_scheduler.py")
        print("3. Monitor: tail -f logs/production.log")
        print("\n🚀 GO LAUNCH!")
        return 0
    else:
        print(f"⚠️  {total - passed} TEST(S) FAILED")
        print("=" * 60)
        print("\n❌ System not ready. Fix the issues above.")
        print("\nCommon fixes:")
        print("• Install dependencies: pip install -r requirements.txt")
        print("• Create .env file: copy .env.example .env")
        print("• Add API keys to .env file")
        return 1

if __name__ == "__main__":
    sys.exit(main())
