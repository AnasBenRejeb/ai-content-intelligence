"""Test script for duplicate detection functionality"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.writer import WriterAgent
from memory.base import MemoryStore, MemoryEntry, MemoryType
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_duplicate_detection():
    """Test the duplicate detection system"""
    print("=" * 60)
    print("TESTING DUPLICATE DETECTION SYSTEM")
    print("=" * 60)
    print()
    
    # Initialize memory and agent
    memory_path = Path("memory_store/test_memory.db")
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory = MemoryStore(memory_path)
    
    writer = WriterAgent(memory)
    
    # Test data
    test_articles = [
        {
            "success": True,
            "title": "AI Breakthrough in Medical Diagnosis",
            "content": "Sample content about AI in medicine...",
            "url": "https://example.com/ai-medicine-1"
        },
        {
            "success": True,
            "title": "AI Breakthrough in Medical Diagnosis",  # Exact duplicate
            "content": "Different content but same title...",
            "url": "https://example.com/ai-medicine-1"  # Same URL
        },
        {
            "success": True,
            "title": "AI Breakthrough in Medical Field",  # Similar title
            "content": "Another article about AI...",
            "url": "https://example.com/ai-medicine-2"
        },
        {
            "success": True,
            "title": "Climate Change Impact on Agriculture",  # Different topic
            "content": "Content about climate change...",
            "url": "https://example.com/climate-1"
        },
    ]
    
    print("📝 Test Scenario:")
    print("  1. Generate article: 'AI Breakthrough in Medical Diagnosis'")
    print("  2. Try same title + same URL → Should skip (exact duplicate)")
    print("  3. Try similar title → Should skip (85%+ similarity)")
    print("  4. Generate different article → Should succeed")
    print()
    
    # Run generation
    print("🚀 Running generation batch...")
    print()
    results = writer.generate_batch(test_articles)
    
    # Analyze results
    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    generated = [r for r in results if r.get("success") and not r.get("skipped")]
    skipped = [r for r in results if r.get("skipped")]
    failed = [r for r in results if not r.get("success") and not r.get("skipped")]
    
    print(f"\n✅ Generated: {len(generated)} articles")
    for r in generated:
        print(f"   - {r['title'][:50]}...")
    
    print(f"\n⏭️  Skipped: {len(skipped)} duplicates")
    for r in skipped:
        print(f"   - {r['title'][:50]}... (Reason: {r.get('reason', 'Unknown')})")
    
    print(f"\n❌ Failed: {len(failed)} articles")
    
    # Verify expectations
    print()
    print("=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    success = True
    
    # Should generate first article
    if len(generated) >= 1 and "AI Breakthrough" in generated[0]['title']:
        print("✅ Test 1 PASSED: First article generated")
    else:
        print("❌ Test 1 FAILED: First article not generated")
        success = False
    
    # Should skip exact duplicate
    if len(skipped) >= 1:
        print("✅ Test 2 PASSED: Exact duplicate skipped")
    else:
        print("❌ Test 2 FAILED: Exact duplicate not skipped")
        success = False
    
    # Should skip similar title
    if len(skipped) >= 2:
        print("✅ Test 3 PASSED: Similar title skipped")
    else:
        print("❌ Test 3 FAILED: Similar title not skipped")
        success = False
    
    # Should generate different article
    if len(generated) >= 2 and "Climate" in generated[-1]['title']:
        print("✅ Test 4 PASSED: Different article generated")
    else:
        print("❌ Test 4 FAILED: Different article not generated")
        success = False
    
    print()
    if success:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    
    print()
    print("=" * 60)
    
    # Check memory persistence
    print("\n📊 Memory Check:")
    semantic_memories = [m for m in memory.retrieve_all() if m.type == MemoryType.SEMANTIC]
    print(f"   Stored {len(semantic_memories)} semantic memories")
    
    for mem in semantic_memories[:3]:
        if mem.content.get("action") == "generate_article":
            print(f"   - {mem.content.get('title', 'Unknown')[:40]}...")
    
    print()
    print("💡 Tip: Run this script again to test cross-run duplicate detection!")
    print()


if __name__ == "__main__":
    test_duplicate_detection()
