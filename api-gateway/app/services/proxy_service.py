import httpx
from fastapi import Request, Response
import logging

logger = logging.getLogger(__name__)

class ProxyService:
    """Handles proxying requests to backend services"""
         
    # Service registry
    SERVICE_ROUTES = {
        "/auth": "http://localhost:8081",
        "/api/users": "http://localhost:8081",
        "/api/transactions": "http://localhost:8082",     
        "/api/wallets": "http://localhost:8088",
        "/api/notify": "http://localhost:8084",
        "/api/rewards": "http://localhost:8089",
    }    
    
    
    async def proxy_request(self, request: Request) -> Response:
        """
        Proxy the request to the appropriate backend service
        """
        target_url = self._get_target_url(request.url.path)
        
        if not target_url:
            return Response(content="Service not found", status_code=404)
        
        full_url = f"{target_url}{request.url.path}"
        if request.url.query:
            full_url = f"{full_url}?{request.url.query}"
            
        headers = dict(request.headers)    
        
        if hasattr(request.state, "user_id"):
            headers["X-User-Id"] = str(request.state.user_id)
            headers["X-User-Email"] = str(request.state.email)
            headers["X-User-Role"] = str(request.state.role)
        
        headers.pop("host", None)
        
        logger.info(f"Proxying {request.method} {request.url.path} -> {full_url}")
        
        async with httpx.AsyncClient() as client:
            try :
                body = await request.body()
                 
                response = await client.request(
                    method=request.method,
                    url=full_url,
                    headers=headers,
                    content=body,
                    timeout=30.0
                ) 
                
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.headers.get("content-type")
                )
            except httpx.RequestError as e:
                logger.error(f"Request error: {e}")
                return Response(
                    content=f"Service unavailable: {str(e)}",
                    status_code=503
                )        
    
    
    def _get_target_url(self, path : str) -> str | None:
        """Get target service URL based on path"""
        for route_prefix, service_url in self.SERVICE_ROUTES.items():
            if path.startswith(route_prefix):
                return service_url
        return None
    

proxy_service = ProxyService()    