# kitchen_receiver.py - Run this on the kitchen laptop
import socket
import json


def listen_for_orders():
    """Simple script to listen for orders from the ordering app"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 5000))  # Listen on port 5000

    print("🍕 KITCHEN ORDER RECEIVER 🍝")
    print("=" * 50)
    print("Listening for orders on port 5000...")
    print("Make sure this laptop is on the same WiFi as the ordering app")
    print("=" * 50)
    print()

    while True:
        try:
            data, addr = sock.recvfrom(4096)
            order_data = json.loads(data.decode('utf-8'))
            formatted_orders = order_data.get("orders", [])

            print("🆕 NEW ORDER RECEIVED!")
            print("─" * 40)
            print("Order data:")
            print(formatted_orders)
            print("─" * 40)
            print(f"Total items: {len(formatted_orders)}")
            print("✅ Order ready for preparation!")
            print()

        except Exception as e:
            print(f"Error receiving order: {e}")


if __name__ == "__main__":
    listen_for_orders()