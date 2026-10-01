from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

app = FastAPI(title="Dual-Panel Network Protocol Visualizer")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join("static", "index.html"))

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
    domain = req.url.split("//")[-1].split("/")[0] if "//" in req.url else req.url.split("/")[0]
    path = "/" + "/".join(req.url.split("/")[1:]) if "/" in req.url else "/"
    
    steps = [
        # Application: DNS
        {"id": 1, "layer": "app", "protocol": "DNS", "direction": "client-to-server", "summary": f"DNS Query: Where is {domain}?", "raw": f"DNS Standard Query A {domain}"},
        {"id": 2, "layer": "app", "protocol": "DNS", "direction": "server-to-client", "summary": "DNS Response: 93.184.216.34", "raw": f"DNS Response: {domain} A 93.184.216.34 (TTL 300)"},
        
        # Transport: TCP Handshake
        {"id": 3, "layer": "transport", "protocol": "TCP", "direction": "client-to-server", "summary": "TCP Handshake: SYN", "raw": "Flags: [SYN] | Seq: 1000 | Ack: 0 | Win: 64240 | Len: 0", "seq": 1000, "ack": 0, "flags": "SYN", "win": 64240},
        {"id": 4, "layer": "transport", "protocol": "TCP", "direction": "server-to-client", "summary": "TCP Handshake: SYN-ACK", "raw": "Flags: [SYN, ACK] | Seq: 5000 | Ack: 1001 | Win: 65535 | Len: 0", "seq": 5000, "ack": 1001, "flags": "SYN-ACK", "win": 65535},
        {"id": 5, "layer": "transport", "protocol": "TCP", "direction": "client-to-server", "summary": "TCP Handshake: ACK", "raw": "Flags: [ACK] | Seq: 1001 | Ack: 5001 | Win: 64240 | Len: 0", "seq": 1001, "ack": 5001, "flags": "ACK", "win": 64240},
        
        # Application & Transport Data Stream
        {"id": 6, "layer": "app", "protocol": "HTTP", "direction": "client-to-server", "summary": f"HTTP GET {path}", "raw": f"GET {path} HTTP/1.1\r\nHost: {domain}\r\nUser-Agent: Mozilla/5.0\r\nAccept: text/html\r\n\r\n"},
        {"id": 7, "layer": "transport", "protocol": "TCP", "direction": "client-to-server", "summary": "TCP Data Segment (HTTP Request)", "raw": "Flags: [PSH, ACK] | Seq: 1001 | Ack: 5001 | Win: 64240 | Len: 120", "seq": 1001, "ack": 5001, "flags": "PSH-ACK", "win": 64240},
        {"id": 8, "layer": "app", "protocol": "HTTP", "direction": "server-to-client", "summary": "HTTP 200 OK (Response)", "raw": "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length: 1256\r\n\r\n<!DOCTYPE html><html>...</html>"},
        {"id": 9, "layer": "transport", "protocol": "TCP", "direction": "server-to-client", "summary": "TCP Data Segment (HTTP Body)", "raw": "Flags: [PSH, ACK] | Seq: 5001 | Ack: 1121 | Win: 65535 | Len: 1256", "seq": 5001, "ack": 1121, "flags": "PSH-ACK", "win": 65535},
        
        # Transport: TCP Teardown
        {"id": 10, "layer": "transport", "protocol": "TCP", "direction": "client-to-server", "summary": "TCP Teardown: FIN-ACK", "raw": "Flags: [FIN, ACK] | Seq: 1121 | Ack: 6257 | Win: 64240 | Len: 0", "seq": 1121, "ack": 6257, "flags": "FIN-ACK", "win": 64240},
        {"id": 11, "layer": "transport", "protocol": "TCP", "direction": "server-to-client", "summary": "TCP Teardown: ACK", "raw": "Flags: [ACK] | Seq: 6257 | Ack: 1122 | Win: 65535 | Len: 0", "seq": 6257, "ack": 1122, "flags": "ACK", "win": 65535}
    ]
    return {"activity": "Browsing", "details": f"Loaded web content from {domain}", "steps": steps}

@app.post("/api/simulate/mail")
def simulate_mail(req: MailRequest):
    steps = [
        # Application: DNS lookup for MX
        {"id": 1, "layer": "app", "protocol": "DNS", "direction": "client-to-server", "summary": "DNS MX Query: mail server address", "raw": f"DNS Query MX for domain of {req.to}"},
        {"id": 2, "layer": "app", "protocol": "DNS", "direction": "server-to-client", "summary": "DNS Response: MX mail.university.edu", "raw": "DNS Answer MX 10 mail.university.edu (IP: 192.0.2.25)"},
        
        # Transport: TCP Handshake
        {"id": 3, "layer": "transport", "protocol": "TCP", "direction": "client-to-server", "summary": "TCP Handshake: SYN", "raw": "Flags: [SYN] | Seq: 2000 | Ack: 0 | Win: 64240 | Len: 0", "seq": 2000, "ack": 0, "flags": "SYN", "win": 64240},
        {"id": 4, "layer": "transport", "protocol": "TCP", "direction": "server-to-client", "summary": "TCP Handshake: SYN-ACK", "raw": "Flags: [SYN, ACK] | Seq: 7000 | Ack: 2001 | Win: 65535 | Len: 0", "seq": 7000, "ack": 2001, "flags": "SYN-ACK", "win": 65535},
        {"id": 5, "layer": "transport", "protocol": "TCP", "direction": "client-to-server", "summary": "TCP Handshake: ACK", "raw": "Flags: [ACK] | Seq: 2001 | Ack: 7001 | Win: 64240 | Len: 0", "seq": 2001, "ack": 7001, "flags": "ACK", "win": 64240},
        
        # SMTP Exchange over TCP
        {"id": 6, "layer": "app", "protocol": "SMTP", "direction": "server-to-client", "summary": "220 mail.university.edu ESMTP Ready", "raw": "220 mail.university.edu ESMTP Service Ready"},
        {"id": 7, "layer": "app", "protocol": "SMTP", "direction": "client-to-server", "summary": "EHLO client.local", "raw": "EHLO client.local"},
        {"id": 8, "layer": "app", "protocol": "SMTP", "direction": "client-to-server", "summary": f"MAIL FROM: <student@local.edu>", "raw": "MAIL FROM: <student@local.edu>"},
        {"id": 9, "layer": "app", "protocol": "SMTP", "direction": "client-to-server", "summary": f"RCPT TO: <{req.to}>", "raw": f"RCPT TO: <{req.to}>"},
        {"id": 10, "layer": "app", "protocol": "SMTP", "direction": "client-to-server", "summary": "DATA Payload Transmission", "raw": f"DATA\r\nSubject: {req.subject}\r\n\r\n{req.body}\r\n."},
        {"id": 11, "layer": "transport", "protocol": "TCP", "direction": "client-to-server", "summary": "TCP Segment carrying SMTP DATA Payload", "raw": f"Flags: [PSH, ACK] | Seq: 2001 | Ack: 7001 | Win: 64240 | Len: {len(req.body)}", "seq": 2001, "ack": 7001, "flags": "PSH-ACK", "win": 64240},
        {"id": 12, "layer": "app", "protocol": "SMTP", "direction": "server-to-client", "summary": "250 2.0.0 Message accepted for delivery", "raw": "250 2.0.0 OK 1728392019 Message Accepted"},
        
        # Transport: TCP Teardown
        {"id": 13, "layer": "transport", "protocol": "TCP", "direction": "client-to-server", "summary": "TCP Teardown: FIN-ACK", "raw": "Flags: [FIN, ACK] | Seq: 2150 | Ack: 7050 | Win: 64240 | Len: 0", "seq": 2150, "ack": 7050, "flags": "FIN-ACK", "win": 64240},
        {"id": 14, "layer": "transport", "protocol": "TCP", "direction": "server-to-client", "summary": "TCP Teardown: ACK", "raw": "Flags: [ACK] | Seq: 7050 | Ack: 2151 | Win: 65535 | Len: 0", "seq": 7050, "ack": 2151, "flags": "ACK", "win": 65535}
    ]
    return {"activity": "Mail", "details": f"Email delivered to {req.to}", "steps": steps}

@app.post("/api/simulate/stream")
def simulate_stream(req: StreamRequest):
    steps = [
        # Application: DNS
        {"id": 1, "layer": "app", "protocol": "DNS", "direction": "client-to-server", "summary": "DNS Query: cdn.streamvideo.com", "raw": "DNS Query A cdn.streamvideo.com"},
        {"id": 2, "layer": "app", "protocol": "DNS", "direction": "server-to-client", "summary": "DNS Response: 198.51.100.12", "raw": "DNS Response: cdn.streamvideo.com A 198.51.100.12"},
        
        # Transport: TCP Handshake
        {"id": 3, "layer": "transport", "protocol": "TCP", "direction": "client-to-server", "summary": "TCP Handshake: SYN", "raw": "Flags: [SYN] | Seq: 3000 | Ack: 0 | Win: 64240 | Len: 0", "seq": 3000, "ack": 0, "flags": "SYN", "win": 64240},
        {"id": 4, "layer": "transport", "protocol": "TCP", "direction": "server-to-client", "summary": "TCP Handshake: SYN-ACK", "raw": "Flags: [SYN, ACK] | Seq: 8000 | Ack: 3001 | Win: 65535 | Len: 0", "seq": 8000, "ack": 3001, "flags": "SYN-ACK", "win": 65535},
        
        # App: Playlist Manifest Fetch (HLS)
        {"id": 5, "layer": "app", "protocol": "HTTP/HLS", "direction": "client-to-server", "summary": "Fetch Playlist Manifest (.m3u8)", "raw": f"GET /stream/{req.quality}/master.m3u8 HTTP/1.1\r\nHost: cdn.streamvideo.com\r\n\r\n"},
        {"id": 6, "layer": "app", "protocol": "HTTP/HLS", "direction": "server-to-client", "summary": f"Return {req.quality} Manifest Data", "raw": f"#EXTM3U\r\n#EXT-X-TARGETDURATION:4\r\n#EXTINF:4.0,\r\nsegment0.ts\r\n#EXTINF:4.0,\r\nsegment1.ts"},
        
        # Transport Data Segments
        {"id": 7, "layer": "transport", "protocol": "TCP", "direction": "server-to-client", "summary": "TCP Video Chunk Transfer (Segment 0.ts)", "raw": "Flags: [ACK] | Seq: 8001 | Ack: 3100 | Win: 65535 | Len: 40960", "seq": 8001, "ack": 3100, "flags": "ACK", "win": 65535},
        {"id": 8, "layer": "transport", "protocol": "UDP", "direction": "server-to-client", "summary": "[UDP Illustrative Alternative] Datagram Stream", "raw": "Src Port: 5004 | Dst Port: 40001 | Length: 1316 | Checksum: 0x41a2 (No reliable handshake/acknowledgments)"},
        {"id": 9, "layer": "transport", "protocol": "TCP", "direction": "server-to-client", "summary": "TCP Video Chunk Transfer (Segment 1.ts)", "raw": "Flags: [ACK] | Seq: 48961 | Ack: 3100 | Win: 65535 | Len: 40960", "seq": 48961, "ack": 3100, "flags": "ACK", "win": 65535}
    ]
    return {"activity": "Streaming", "details": f"Streaming video content at {req.quality}", "steps": steps}
           