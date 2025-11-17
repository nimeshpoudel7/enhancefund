#!/usr/bin/env python3
"""
Quick WebSocket connection test script
Run this to test if WebSocket connection works
"""
import asyncio
import websockets
import json

async def test_websocket():
    token = "aec8e0e9a0b3d8637b8926a5adffb44e487330ec"
    uri = f"ws://127.0.0.1:8000/ws/notifications/?token={token}"
    
    print(f"🔗 Connecting to: {uri}")
    print("=" * 60)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            print("=" * 60)
            
            # Wait for connection message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📨 Received: {json.dumps(data, indent=2)}")
                
                if data.get('type') == 'connection':
                    print("✅ Connection confirmed by server!")
            except asyncio.TimeoutError:
                print("⚠️ No connection message received within 5 seconds")
            
            # Send ping
            print("\n📤 Sending ping...")
            await websocket.send(json.dumps({"type": "ping"}))
            
            # Wait for pong
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📨 Received: {json.dumps(data, indent=2)}")
                
                if data.get('type') == 'pong':
                    print("✅ Ping/Pong working!")
            except asyncio.TimeoutError:
                print("⚠️ No pong received within 5 seconds")
            
            # Keep connection alive for a few seconds
            print("\n⏳ Keeping connection alive for 10 seconds...")
            print("   (You can trigger a notification in another terminal)")
            await asyncio.sleep(10)
            
            print("\n✅ Test completed successfully!")
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Connection failed with status code: {e.status_code}")
        print(f"   Response headers: {e.headers}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: Code {e.code}, Reason: {e.reason}")
    except ConnectionRefusedError:
        print("❌ Connection refused - Is the server running?")
        print("   Make sure you're running: daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 WebSocket Connection Test")
    print("=" * 60)
    asyncio.run(test_websocket())

