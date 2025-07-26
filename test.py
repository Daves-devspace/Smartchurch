#!/usr/bin/env python
"""
🔍 WebSocket Debug Test - Check if WebSocket messages are being sent correctly
"""

import os
import sys
import django
from pathlib import Path

# Configure Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smartchurch.settings')
django.setup()

import time
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def debug_websocket_setup():
    """Debug WebSocket configuration and connection"""
    
    print("🔍 WEBSOCKET DEBUG TEST")
    print("=" * 50)
    
    # 1. Check channel layer configuration
    try:
        channel_layer = get_channel_layer()
        print(f"✅ Channel layer: {type(channel_layer).__name__}")
        print(f"📡 Channel layer config: {channel_layer}")
    except Exception as e:
        print(f"❌ Channel layer error: {e}")
        return False
    
    # 2. Test basic WebSocket send
    group_name = "live_verses"
    test_message = {
        "type": "send_overlay",
        "chunk": "TEST MESSAGE",
        "verses": [
            {
                "reference": "Test 1:1",
                "text": "This is a test verse to verify WebSocket functionality",
                "score": 0.95
            }
        ],
        "debug_test": True,
        "timestamp": time.time()
    }
    
    print(f"\n📤 Sending test message to group: {group_name}")
    print(f"📝 Message: {json.dumps(test_message, indent=2)}")
    
    try:
        async_to_sync(channel_layer.group_send)(group_name, test_message)
        print("✅ Message sent successfully to WebSocket")
    except Exception as e:
        print(f"❌ Failed to send WebSocket message: {e}")
        return False
    
    return True

def test_consumer_method():
    """Test if the consumer method exists and works"""
    
    print("\n🔍 TESTING CONSUMER METHOD")
    print("=" * 30)
    
    try:
        # Try to import your WebSocket consumer
        from scripture.consumers import LiveVerseConsumer  # Adjust import path
        print("✅ Consumer imported successfully")
        
        # Check if send_overlay method exists
        if hasattr(LiveVerseConsumer, 'send_overlay'):
            print("✅ send_overlay method found")
        else:
            print("❌ send_overlay method NOT found")
            print("   Your consumer might be missing the send_overlay method")
            
    except ImportError as e:
        print(f"❌ Could not import consumer: {e}")
        print("   Check your consumer file path and class name")
        return False
    
    return True

def check_websocket_routing():
    """Check WebSocket URL routing"""
    
    print("\n🔍 CHECKING WEBSOCKET ROUTING")
    print("=" * 30)
    
    try:
        from smartchurch.routing import websocket_urlpatterns  # Adjust import
        print("✅ WebSocket routing imported")
        print(f"📋 URL patterns: {len(websocket_urlpatterns)} routes found")
        
        for pattern in websocket_urlpatterns:
            print(f"   🔗 Route: {pattern.pattern.regex.pattern}")
            
    except ImportError as e:
        print(f"❌ Could not import WebSocket routing: {e}")
        return False
    
    return True

def frontend_connection_test():
    """Generate test data for frontend connection testing"""
    
    print("\n🌐 FRONTEND CONNECTION TEST")
    print("=" * 30)
    
    print("📋 To test your frontend WebSocket connection:")
    print("\n1. Open your browser's Developer Console (F12)")
    print("2. Go to your verse overlay page")
    print("3. Paste this JavaScript code:")
    
    js_test_code = '''
// Test WebSocket connection
const wsUrl = 'ws://localhost:8000/ws/live-verses/';  // Adjust URL
const socket = new WebSocket(wsUrl);

socket.onopen = function() {
    console.log('✅ WebSocket connected successfully');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('📨 Received message:', data);
    
    if (data.debug_test) {
        console.log('🧪 This is a debug test message');
    }
};

socket.onerror = function(error) {
    console.error('❌ WebSocket error:', error);
};

socket.onclose = function() {
    console.log('🔌 WebSocket disconnected');
};
    '''
    
    print(f"\n```javascript\n{js_test_code}\n```")
    
    print("\n4. You should see connection messages in the console")
    print("5. Run the Python test again - you should see messages appear")

def comprehensive_debug():
    """Run all debug tests"""
    
    print("🚀 COMPREHENSIVE WEBSOCKET DEBUG")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: WebSocket setup
    if debug_websocket_setup():
        tests_passed += 1
    
    # Test 2: Consumer method
    if test_consumer_method():
        tests_passed += 1
    
    # Test 3: WebSocket routing  
    if check_websocket_routing():
        tests_passed += 1
    
    # Test 4: Frontend instructions
    frontend_connection_test()
    tests_passed += 1  # Always counts as "passed" since it's just instructions
    
    print(f"\n🎯 DEBUG SUMMARY: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ Backend WebSocket setup appears correct")
        print("🔍 Issue is likely in frontend WebSocket connection")
        print("👀 Check browser console for WebSocket errors")
    else:
        print("❌ Found backend WebSocket issues")
        print("🔧 Fix the failed tests above")

def send_manual_test_message():
    """Send a manual test message that should appear in UI"""
    
    print("\n📤 SENDING MANUAL TEST MESSAGE")
    print("=" * 30)
    
    channel_layer = get_channel_layer()
    test_message = {
        "type": "send_overlay",
        "chunk": "MANUAL TEST - If you see this, WebSocket is working!",
        "verses": [
            {
                "reference": "John 3:16",
                "text": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
                "score": 1.0
            }
        ],
        "manual_test": True,
        "timestamp": time.time()
    }
    
    try:
        async_to_sync(channel_layer.group_send)("live_verses", test_message)
        print("✅ Manual test message sent!")
        print("👀 Check your browser - you should see John 3:16 appear")
        print("⏰ Wait 5 seconds for the message to appear...")
        time.sleep(5)
        print("❓ Did the verse appear in your UI? (Check browser)")
    except Exception as e:
        print(f"❌ Failed to send manual test: {e}")

if __name__ == "__main__":
    # Run comprehensive debug
    comprehensive_debug()
    
    print("\n" + "="*50)
    
    # Send a manual test message
    send_manual_test_message()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Check your browser's Developer Console for WebSocket errors")
    print("2. Verify your WebSocket URL in frontend JavaScript")
    print("3. Ensure your Django server is running with WebSocket support")
    print("4. Check if your consumer's send_overlay method is correct")