import requests
import hashlib
import time
from typing import Dict, Any

class APIClient:
    def __init__(self, base_url: str = "https://assist.weinpay.com"):
        self.base_url = base_url
        
    def _generate_signature(self, timestamp: int, data: Dict[str, Any]) -> str:
        """Generate signature for the request"""
        # TODO: Implement actual signature logic based on your requirements
        # This is a placeholder implementation
        return "8FD39EABE64DC7E6F56953FD8EE5B31C"
    
    def get_member_operate_list(self, 
                              page: int = 1, 
                              limit: int = 10,
                              team: str = "wining") -> Dict[str, Any]:
        """
        Get member operation list from the API
        """
        payload = {
            "timestamp": 1722579064,
            "signed": self._generate_signature(1722579064, {}),
            "page": page,
            "limit": limit,
            "client_id": "shizhongqi@gmail.com",
            #"unique_id": int(time.time()),
            "unique_id": 1741594600,
            "team": team
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{self.base_url}/api/PyHandle/memberOperateList",
            json=payload,
            headers=headers
        )
        
        response.raise_for_status()  # Raise exception for non-200 status codes
        return response.json() 