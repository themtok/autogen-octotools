from pydantic import BaseModel, Field
from otools_autogen.tools import Tool, ToolCard
import json
import urllib.request
from typing import Optional, Dict



class APICallerToolRequest(BaseModel):
    url: str = Field(None, description="API endpoint URL")
    params: Optional[Dict] = Field(None, description="Parameters to be sent in the API request")
    headers: Optional[Dict] = Field(None, description="Headers to be sent in the API request")
    method: str = Field("GET", description="HTTP method to be used for the API request (GET, POST, PUT, DELETE)")
    body: Optional[Dict] = Field(None, description="Body to be sent in the API request (for POST, PUT methods)")
    
class APICallerToolResponse(BaseModel):
    success: bool = Field(None, description="If the API call was successful")
    response: Optional[str] = Field(None, description="Response from the API call")
    error: str = Field(None, description="Error message if the API call failed")
 

tool_card = ToolCard(
    tool_id="APICallerTool",
    name="API Caller Tool",
    description="Tool for calling an API with a given URL and parameters. Returns the response from the API. Accepts only json data for the body of the request.",
    inputs=APICallerToolRequest,
    outputs=APICallerToolResponse,
    user_metadata={},
    demo_input=[
        APICallerToolRequest(
            url="https://jsonplaceholder.typicode.com/posts",
            params={"userId": 1},
            headers={"Content-Type": "application/json"},
            method="GET"
        ),
        APICallerToolRequest(
            url="https://jsonplaceholder.typicode.com/posts",
            headers={"Content-Type": "application/json"},
            method="POST",
            body={"title": "foo", "body": "bar", "userId": 1}
        )
            
    ]
)

   
    
class APICallerTool(Tool):
    @property
    def card(self) -> ToolCard:
        return tool_card
    
    
    async def run(self, inputs: APICallerToolRequest) -> APICallerToolResponse:
        url = inputs.url
        headers = inputs.headers if inputs.headers else {}
        params = inputs.params if inputs.params else {}
        method = inputs.method.upper()
        
        if method == "GET":
            request = urllib.request.Request(url, headers=headers, method=method)
            if params:
                url += "?" + urllib.parse.urlencode(params)
        else:
            json_data = json.dumps(inputs.body).encode("utf-8")
            request = urllib.request.Request(url, data=json_data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(request) as response:
                response_body = response.read().decode("utf-8")
                return APICallerToolResponse.model_validate({
                    "success": True,
                    "response": response_body,
                    "error": None
                })
        except Exception as e:
            return APICallerToolResponse.model_validate({
                "success": False,
                "error": str(e)
            })
            