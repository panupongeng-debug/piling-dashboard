#!/usr/bin/env python3
"""
Simple HTTP Server for Piling Dashboard
Run this to open dashboard at http://localhost:8000
"""

import http.server
import socketserver
import webbrowser
import os
import time

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Prevent caching to always get latest data
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

if __name__ == '__main__':
    os.chdir(DIRECTORY)

    print("=" * 60)
    print("🚀 Piling Dashboard Server")
    print("=" * 60)
    print(f"📁 Directory: {DIRECTORY}")
    print(f"🌐 Dashboard: http://localhost:{PORT}/piling_dashboard.html")
    print(f"📊 Data: http://localhost:{PORT}/Data/pile_data.json")
    print()
    print("💡 Workflow:")
    print("  1. Edit Excel: D:\\Daily Report\\Data\\Pile Log.xlsx")
    print("  2. Run update: python update_pile_dashboard.py")
    print("  3. Refresh browser (Ctrl+F5)")
    print("  4. See new data!")
    print()
    print("❌ To stop: Close this window or press Ctrl+C")
    print("=" * 60)
    print()

    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"✅ Server started on port {PORT}")
        print(f"🌐 Opening browser in 2 seconds...")
        print()

        time.sleep(2)

        try:
            webbrowser.open(f'http://localhost:{PORT}')
        except:
            print("⚠️ Could not open browser automatically")
            print(f"📌 Please open: http://localhost:{PORT}/piling_dashboard.html manually")

        print("⏳ Server running... Press Ctrl+C to stop")
        print()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✅ Server stopped")
