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
                "protocol": "TCP SYN",
                "direction": "client-to-server",
                "summary": "TCP Handshake [SYN]",
                "raw": "Client -> Server [SYN] Seq=0 Win=64240 Len=0 MSS=1460 (Port 80)"
            },
            {
                "id": 4,
                "protocol": "TCP SYN-ACK",
                "direction": "server-to-client",
                "summary": "TCP Handshake [SYN, ACK]",
                "raw": "Server -> Client [SYN, ACK] Seq=0 Ack=1 Win=65535 Len=0 MSS=1460"
            },
            {
                "id": 5,
                "protocol": "TCP ACK",
                "direction": "client-to-server",
                "summary": "TCP Handshake [ACK]",
                "raw": "Client -> Server [ACK] Seq=1 Ack=1 Win=64240 Len=0"
            },
            {
                "id": 6,
                "protocol": "HTTP Request",
                "direction": "client-to-server",
                "summary": f"GET / HTTP/1.1",
                "raw": f"GET / HTTP/1.1\r\nHost: {domain}\r\nUser-Agent: VisualizerBrowser/1.0\r\nAccept: text/html\r\n\r\n"
            },
            {
                "id": 7,
                "protocol": "HTTP Response",
                "direction": "server-to-client",
                "summary": "HTTP/1.1 200 OK",
                "raw": "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length: 1256\r\nServer: ECS (scl/e05b)\r\n\r\n<!DOCTYPE html><html>...</html>"
            }
        ]
    }

@app.post("/api/simulate/mail")
def simulate_mail(req: MailRequest):
    mail_domain = req.to.split('@')[-1] if '@' in req.to else 'smtp-server.com'
    return {
        "activity": "Mail",
        "details": f"Sent mail to {req.to}",
        "steps": [
            # 1. DNS Resolution
            {
                "id": 1,
                "protocol": "DNS Query",
                "direction": "client-to-server",
                "summary": f"Query MX mail.{mail_domain}",
                "raw": f"DNS Query: ID 0x1a2b, Query MX mail.{mail_domain}"
            },
            {
                "id": 2,
                "protocol": "DNS Response",
                "direction": "server-to-client",
                "summary": f"MX response -> mail.{mail_domain} [192.0.2.25]",
                "raw": f"DNS Response: ID 0x1a2b, MX 10 mail.{mail_domain} -> 192.0.2.25"
            },
            # 2. TCP Handshake
            {
                "id": 3,
                "protocol": "TCP SYN",
                "direction": "client-to-server",
                "summary": "TCP Handshake [SYN]",
                "raw": "Client -> Mail Server [SYN] Seq=0 Win=64240 Len=0 MSS=1460 (Port 25)"
            },
            {
                "id": 4,
                "protocol": "TCP SYN-ACK",
                "direction": "server-to-client",
                "summary": "TCP Handshake [SYN, ACK]",
                "raw": "Mail Server -> Client [SYN, ACK] Seq=0 Ack=1 Win=65535 Len=0"
            },
            {
                "id": 5,
                "protocol": "TCP ACK",
                "direction": "client-to-server",
                "summary": "TCP Handshake [ACK]",
                "raw": "Client -> Mail Server [ACK] Seq=1 Ack=1 Win=64240 Len=0"
            },
            # 3. SMTP Exchange
            {
                "id": 6,
                "protocol": "SMTP Response",
                "direction": "server-to-client",
                "summary": f"220 mail.{mail_domain} ESMTP Service Ready",
                "raw": f"S: 220 mail.{mail_domain} ESMTP Service Ready"
            },
            {
                "id": 7,
                "protocol": "SMTP EHLO",
                "direction": "client-to-server",
                "summary": "EHLO client.local",
                "raw": "C: EHLO client.local"
            },
            {
                "id": 8,
                "protocol": "SMTP Response",
                "direction": "server-to-client",
                "summary": "250 Hello Client, pleased to meet you",
                "raw": "S: 250-mail.smtp-server.com\r\nS: 250-PIPELINING\r\nS: 250 8BITMIME"
            },
            {
                "id": 9,
                "protocol": "SMTP MAIL FROM",
                "direction": "client-to-server",
                "summary": "MAIL FROM:<user@localdomain>",
                "raw": "C: MAIL FROM:<user@localdomain>"
            },
            {
                "id": 10,
                "protocol": "SMTP Response",
                "direction": "server-to-client",
                "summary": "250 2.1.0 Sender OK",
                "raw": "S: 250 2.1.0 Sender OK"
            },
            {
                "id": 11,
                "protocol": "SMTP RCPT TO",
                "direction": "client-to-server",
                "summary": f"RCPT TO:<{req.to}>",
                "raw": f"C: RCPT TO:<{req.to}>"
            },
            {
                "id": 12,
                "protocol": "SMTP Response",
                "direction": "server-to-client",
                "summary": "250 2.1.5 Recipient OK",
                "raw": "S: 250 2.1.5 Recipient OK"
            },
            {
                "id": 13,
                "protocol": "SMTP DATA",
                "direction": "client-to-server",
                "summary": "DATA payload initiation",
                "raw": "C: DATA"
            },
            {
                "id": 14,
                "protocol": "SMTP Response",
                "direction": "server-to-client",
                "summary": "354 Start mail input; end with <CR><LF>.<CR><LF>",
                "raw": "S: 354 End data with <CR><LF>.<CR><LF>"
            },
            {
                "id": 15,
                "protocol": "SMTP DATA",
                "direction": "client-to-server",
                "summary": "Send Body Content",
                "raw": f"C: Subject: {req.subject}\r\n\r\n{req.body}\r\n."
            },
            {
                "id": 16,
                "protocol": "SMTP Response",
                "direction": "server-to-client",
                "summary": "250 2.0.0 Message queued for delivery",
                "raw": "S: 250 2.0.0 Ok: queued as 4SyXzL087z1"
            },
            {
                "id": 17,
                "protocol": "SMTP QUIT",
                "direction": "client-to-server",
                "summary": "QUIT session close",
                "raw": "C: QUIT"
            },
            {
                "id": 18,
                "protocol": "SMTP Response",
                "direction": "server-to-client",
                "summary": "221 2.0.0 Bye",
                "raw": "S: 221 2.0.0 Service closing transmission channel"
            },
            # 4. TCP Teardown
            {
                "id": 19,
                "protocol": "TCP FIN",
                "direction": "client-to-server",
                "summary": "TCP Teardown [FIN, ACK]",
                "raw": "Client -> Mail Server [FIN, ACK] Seq=240 Ack=185 Win=64240"
            },
            {
                "id": 20,
                "protocol": "TCP ACK",
                "direction": "server-to-client",
                "summary": "TCP Connection Closed [ACK]",
                "raw": "Mail Server -> Client [ACK] Seq=185 Ack=241 Win=65535"
            }
        ]
    }

@app.post("/api/simulate/stream")
def simulate_stream(req: StreamRequest):
    return {
        "activity": "Streaming",
        "details": f"Quality: {req.quality}",
        "steps": [
            # 1. DNS Resolution
            {
                "id": 1,
                "protocol": "DNS Query",
                "direction": "client-to-server",
                "summary": "Query cdn.stream.com",
                "raw": "DNS Question: cdn.stream.com IN A"
            },
            {
                "id": 2,
                "protocol": "DNS Response",
                "direction": "server-to-client",
                "summary": "Response cdn.stream.com -> 198.51.100.42",
                "raw": "DNS Answer: cdn.stream.com -> 198.51.100.42 (TTL 60)"
            },
            # 2. TCP Handshake
            {
                "id": 3,
                "protocol": "TCP SYN",
                "direction": "client-to-server",
                "summary": "TCP Handshake [SYN]",
                "raw": "Client -> CDN Server [SYN] Seq=0 Win=65535 Len=0 MSS=1460 (Port 443)"
            },
            {
                "id": 4,
                "protocol": "TCP SYN-ACK",
                "direction": "server-to-client",
                "summary": "TCP Handshake [SYN, ACK]",
                "raw": "CDN Server -> Client [SYN, ACK] Seq=0 Ack=1 Win=65535 Len=0"
            },
            {
                "id": 5,
                "protocol": "TCP ACK",
                "direction": "client-to-server",
                "summary": "TCP Handshake [ACK]",
                "raw": "Client -> CDN Server [ACK] Seq=1 Ack=1 Win=65535 Len=0"
            },
            # 3. HTTP HLS Fetching
            {
                "id": 6,
                "protocol": "HTTP GET Manifest",
                "direction": "client-to-server",
                "summary": "GET /stream/playlist.m3u8",
                "raw": f"GET /stream/{req.quality}/playlist.m3u8 HTTP/1.1\r\nHost: cdn.stream.com\r\nUser-Agent: HLSPlayer/2.0"
            },
            {
                "id": 7,
                "protocol": "HTTP Response Manifest",
                "direction": "server-to-client",
                "summary": "200 OK (HLS Playlist Manifest)",
                "raw": "HTTP/1.1 200 OK\r\nContent-Type: application/vnd.apple.mpegurl\r\n\r\n#EXTM3U\r\n#EXT-X-TARGETDURATION:4\r\n#EXTINF:4.0,\r\nchunk_1.ts"
            },
            {
                "id": 8,
                "protocol": "HTTP GET Segment 1",
                "direction": "client-to-server",
                "summary": f"GET /stream/segment1.ts ({req.quality})",
                "raw": f"GET /stream/{req.quality}/seg1.ts HTTP/1.1\r\nHost: cdn.stream.com"
            },
            {
                "id": 9,
                "protocol": "HTTP Response Segment 1",
                "direction": "server-to-client",
                "summary": "200 OK (Media Stream Bytes)",
                "raw": "HTTP/1.1 200 OK\r\nContent-Type: video/MP2T\r\nContent-Length: 1048576\r\n\r\n[Binary Segment Data - 1MB Chunk]"
            },
            # 4. TCP Teardown
            {
                "id": 10,
                "protocol": "TCP FIN",
                "direction": "client-to-server",
                "summary": "TCP Teardown [FIN, ACK]",
                "raw": "Client -> CDN Server [FIN, ACK] Seq=1049 Ack=2048"
            },
            {
                "id": 11,
                "protocol": "TCP ACK",
                "direction": "server-to-client",
                "summary": "TCP Connection Closed [ACK]",
                "raw": "CDN Server -> Client [ACK] Seq=2048 Ack=1050"
            }
        ]
    }