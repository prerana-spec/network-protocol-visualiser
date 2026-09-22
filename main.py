from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="Protocol Visualizer Dashboard")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

class BrowseRequest(BaseModel):
    url: str

class MailRequest(BaseModel):
    to: str
    subject: str
    body: str

class StreamRequest(BaseModel):
    quality: str

@app.post("/api/simulate/browse")
def simulate_browse(req: BrowseRequest):
    domain = req.url.replace("https://", "").replace("http://", "").split('/')[0] or "example.com"
    return {
        "activity": "Browsing",
        "details": f"Visited: {req.url}",
        "steps": [
            {
                "id": 1,
                "protocol": "DNS Query",
                "direction": "client-to-server",
                "summary": f"Standard query A {domain}",
                "raw": f"DNS Header: ID 0x82f1, Flags 0x0100 (Standard Query)\nQuestion: {domain} IN A"
            },
            {
                "id": 2,
                "protocol": "DNS Response",
                "direction": "server-to-client",
                "summary": f"Standard response A {domain} -> 93.184.216.34",
                "raw": f"DNS Header: ID 0x82f1, Flags 0x8180 (No error)\nAnswer: {domain} -> 93.184.216.34 (TTL 300)"
            },
            {
                "id": 3,
                "protocol": "HTTP Request",
                "direction": "client-to-server",
                "summary": f"GET / HTTP/1.1",
                "raw": f"GET / HTTP/1.1\r\nHost: {domain}\r\nUser-Agent: VisualizerBrowser/1.0\r\nAccept: text/html\r\n\r\n"
            },
            {
                "id": 4,
                "protocol": "HTTP Response",
                "direction": "server-to-client",
                "summary": "HTTP/1.1 200 OK",
                "raw": "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length: 1256\r\nServer: ECS (scl/e05b)\r\n\r\n<!DOCTYPE html><html>...</html>"
            }
        ]
    }

@app.post("/api/simulate/mail")
def simulate_mail(req: MailRequest):
    return {
        "activity": "Mail",
        "details": f"Sent mail to {req.to}",
        "steps": [
            {"id": 1, "protocol": "DNS Query", "direction": "client-to-server", "summary": "Query MX mail.smtp-server.com", "raw": "DNS Query: MX mail.smtp-server.com"},
            {"id": 2, "protocol": "SMTP EHLO", "direction": "client-to-server", "summary": "EHLO client.local", "raw": "C: EHLO client.local"},
            {"id": 3, "protocol": "SMTP Response", "direction": "server-to-client", "summary": "220 mail.smtp-server.com ESMTP ready", "raw": "S: 220 mail.smtp-server.com ESMTP Service Ready"},
            {"id": 4, "protocol": "SMTP MAIL FROM", "direction": "client-to-server", "summary": "MAIL FROM:<user@local>", "raw": "C: MAIL FROM:<user@domain.com>"},
            {"id": 5, "protocol": "SMTP RCPT TO", "direction": "client-to-server", "summary": f"RCPT TO:<{req.to}>", "raw": f"C: RCPT TO:<{req.to}>"},
            {"id": 6, "protocol": "SMTP DATA", "direction": "client-to-server", "summary": "DATA payload transfer", "raw": f"C: DATA\r\nSubject: {req.subject}\r\n\r\n{req.body}\r\n."},
            {"id": 7, "protocol": "SMTP QUIT", "direction": "client-to-server", "summary": "QUIT connection closed", "raw": "C: QUIT\r\nS: 221 2.0.0 Bye"}
        ]
    }

@app.post("/api/simulate/stream")
def simulate_stream(req: StreamRequest):
    return {
        "activity": "Streaming",
        "details": f"Quality: {req.quality}",
        "steps": [
            {"id": 1, "protocol": "DNS Query", "direction": "client-to-server", "summary": "Query cdn.stream.com", "raw": "DNS Question: cdn.stream.com IN A"},
            {"id": 2, "protocol": "HTTP GET Manifest", "direction": "client-to-server", "summary": "GET /stream/playlist.m3u8", "raw": "GET /stream/playlist.m3u8 HTTP/1.1\r\nHost: cdn.stream.com"},
            {"id": 3, "protocol": "HTTP Response Manifest", "direction": "server-to-client", "summary": "200 OK (HLS Manifest)", "raw": "HTTP/1.1 200 OK\r\n#EXTM3U\r\n#EXT-X-STREAM-INF:BANDWIDTH=800000\r\nchunk_1.ts"},
            {"id": 4, "protocol": "HTTP GET Segment 1", "direction": "client-to-server", "summary": f"GET /stream/segment1.ts ({req.quality})", "raw": f"GET /stream/{req.quality}/seg1.ts HTTP/1.1"},
            {"id": 5, "protocol": "HTTP Response Segment 1", "direction": "server-to-client", "summary": "200 OK (Media Stream Bytes)", "raw": "HTTP/1.1 200 OK\r\nContent-Type: video/MP2T\r\n[Binary Segment Data]"}
        ]
    }