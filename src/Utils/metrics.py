from prometheus_client import Counter, Histogram , generate_latest , CONTENT_TYPE_LATEST
from fastapi import FastAPI, Fastapi , Request , Response
import starlette.middleware.base as BaseHTTPMiddleware
import time

# define metrics 
REQUEST_COUNT = Counter('request_count', 'Total number of requests', ['method', 'endpoint','status'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Latency of requests in seconds', ['method', 'endpoint'])

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # we have request that will go and return response and we want to calculate the latency of that request
        start_time = time.time()
        # process the request and get the response and check wich function is called and how much time it takes to execute that function and then we will update the metrics
        response = await call_next(request)
        latency = time.time() - start_time
        
        # we should grab the endponit url : for exemple if we have ("/upload/1") --> upload_data function will be called 
        endpoint = request.url.path
        
        REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, status=response.status_code).inc()
        REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(latency)
        # very important 
        return response
    
# this midddle require a function to link it to fastapi application and this function will be called when we want to expose the metrics endpoint
def setup_metrics(app: FastAPI):
    "setup the prometheus middleware and the metrics endpoint"
    # Add Prometheus middleware 
    app.add_middleware(PrometheusMiddleware)
    # prometheus need from the app an endpoint to expose the metrics
    # that's why we will create an endpoint to expose the metrics and set include_in_schema to false because we don't want to show it in the documentation and it is sensitive endpoint
    # @app.get("/metrics" , include_in_schema=False) -> /metrics is not secure endpoint because it can be accessed by anyone.
    # for that we will make a different name hard to guess to prevent any unauthorized acess   
    @app.get("/tgshsqjhsjk_m5hsbswhbswkh7hs" , include_in_schema=False)
    
    async def metrics():
        # we will return the metrics in the response and set the content type to the prometheus format
        # generate_latest() is a function from prometheus client that will generate the metrics in the prometheus format
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)