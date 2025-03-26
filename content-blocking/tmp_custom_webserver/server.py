import http.server
import socketserver
import mimetypes

PORT = 8000

mimetypes.add_type("application/javascript", ".js")

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/script1.js":
            # Serve the first script dynamically
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.end_headers()
            self.wfile.write(b"""
            eval("console.log('Script 1 loaded'); const script2 = document.createElement('script'); script2.src = '/script2.js'; document.body.appendChild(script2);")
            const code = `
            const canvas = document.createElement("canvas");
            canvas.width = 200;
            canvas.height = 200;
            canvas.style.border = "1px solid black";
            document.body.appendChild(canvas);
            const ctx = canvas.getContext("2d");

            // Draw a red dot in the center
            ctx.fillStyle = "red";
            ctx.beginPath();
            ctx.arc(canvas.width / 2, canvas.height / 2, 5, 0, Math.PI * 2);
            ctx.fill();

            // Get canvas information
            console.log("Canvas Width:", canvas.width);
            console.log("Canvas Height:", canvas.height);

            // Get pixel data from the center of the canvas
            const pixelData = ctx.getImageData(canvas.width / 2, canvas.height / 2, 1, 1).data;
            console.log("Pixel Data at Center:", pixelData);
            `;

            eval(code);
            """)
        elif self.path == "/script2.js":
            # Serve the second script dynamically
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.end_headers()
            self.wfile.write(b"""
            console.log('Script 2 loaded');
            const content = document.createElement('div');
            content.textContent = 'Content loaded by script2.js';
            document.body.appendChild(content);
            """)

        elif self.path == "/image":
            # Serve the SVG image
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            self.wfile.write(b"""
    <script>
        window.onload = function() {
            setTimeout(function() {
                var img = document.createElement('img');
                img.src = 'data:image/svg+xml,%3Csvg viewBox=%220 0 36 36%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cpath d=%22M7,7l22,11L7,29V7z%22 fill=%22%23FFF%22/%3E%3C/svg%3E';
                img.alt = '';
                document.body.appendChild(img);
            }, 0);
        };
    </script>
""")
        elif self.path == "/redirect":
            # Redirect to another page
            self.send_response(302)  # HTTP 302 Found (temporary redirect)
            self.send_header("Location", "https://zpravy.idnes.cz")  # Target URL
            self.end_headers()

        else:
            # Fall back to serving static files
            super().do_GET()

# Create and start the server
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()