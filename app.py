from flask import Flask, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency",
    ["endpoint"]
)

@app.route("/")
def hello():
    REQUEST_COUNT.labels("GET", "/").inc()
    return "Hello from Flask running in kubernetes (kind) with Metrics from Argo CD!"

@app.route("/health")
def health():
    REQUEST_COUNT.labels("GET", "/health").inc()
    return {"status": "ok"}

@app.route("/metrics")
def metrics():
    # Now Response and CONTENT_TYPE_LATEST are defined
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.before_request
def before_request():
    app.start_time = time.time()

@app.after_request
def after_request(response):
    latency = time.time() - app.start_time
    REQUEST_LATENCY.labels(endpoint="/").observe(latency)
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
