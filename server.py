#!/usr/bin/env python3
"""
Local development & verification server for Hans' Water Taxi Widget.
Binds strictly to 127.0.0.1:8080 and provides a CORS proxy endpoint (/api/wsdot-kcm)
for WSDOT's King County Marine live vessel feed (VesselsKCM.ashx).
"""
import http.server
import socketserver
import urllib.request
import json

PORT = 8080
HOST = "127.0.0.1"
WSDOT_KCM_URL = "https://wsdot.com/ferries/vesselwatch/VesselsKCM.ashx"

class WaterTaxiHandler(http.server.SimpleHTTPRequestHandler):
    def address_string(self):
        return self.client_address[0]

    def do_GET(self):
        if self.path.startswith("/api/wsdot-kcm"):
            try:
                req = urllib.request.Request(
                    WSDOT_KCM_URL,
                    headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
                )
                with urllib.request.urlopen(req, timeout=5) as res:
                    payload = res.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(payload)
            except Exception as e:
                self.send_response(502)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            super().do_GET()

if __name__ == "__main__":
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((HOST, PORT), WaterTaxiHandler) as httpd:
        print(f"Serving Hans Water Taxi Widget at http://{HOST}:{PORT}")
        httpd.serve_forever()
