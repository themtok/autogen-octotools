from pydantic import BaseModel, Field
from otools_autogen.tools import Tool, ToolCard
import json
from duckduckgo_search import DDGS



class SearchEngineRequest(BaseModel):
    query: str = Field(None, description="Search query to search for in the search engine")
    max_results: int = Field(5, description="Maximum number of search results to return")
    
class SerchResultItem(BaseModel):
    title: str= Field(None, description="Search engine result title")
    link: str= Field(None, description="Search engine result URL")
    description: str= Field(None, description="Search engine result description, digest ")
class SearchEngingResponse(BaseModel):
    success: bool
    search_results: list[SerchResultItem]= Field(None, description="search engine result items")
    
    
tool_card= ToolCard(
                tool_id="SearchEngineTool",
                description="Tool for performing web search using engine that indexed most of the world's data. Returns search results with title, link and short description.",
                name="Search Engine",
                inputs=SearchEngineRequest,
                outputs=SearchEngingResponse,
                user_metadata={
                    "Comments": "Each result should be checked by fetching the page content and extracting the relevant information. This tool is not responsible for the accuracy of the search results.",
                    },
                demo_input=[
                    SearchEngineRequest(query="Python programming language"),
                    SearchEngineRequest(query="Washington"),
                    SearchEngineRequest(query="Place to visit in the USA")                
                ])

class SearchEngineTool(Tool):
    @property
    def card(self) -> ToolCard:
        return tool_card
    
    
    async def run(self, inputs: SearchEngineRequest) -> SearchEngingResponse:
        results = DDGS(verify=False).text(inputs.query, max_results=inputs.max_results)
        items= [
            SerchResultItem(
                title=result['title'],
                link=result['href'],
                description=result['body']
            ) for result in results
        ]
        return SearchEngingResponse.model_validate({
            "success": True,
            "search_results": items
        })
        
        
        
if __name__ == "__main__":
    async def m():
        m = SearchEngineTool()
        r= await m.run(SearchEngineRequest(query="Python programming language"))
        print(r)
    import asyncio
    asyncio.run(m())
    
    