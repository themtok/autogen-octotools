from otools_autogen.tools import Tool, ToolCard
from pydantic import BaseModel
import wikipedia



class WikipediaSearchRequest(BaseModel):
    query: str
    
class WikipediaSearchResponse(BaseModel):
    success: bool
    search_results: list[str]
    


class WikipediaSearch(Tool):
        @property
        def card(self) -> ToolCard:
            return ToolCard(
                tool_id="WikipediaSearchTool",
                name="Wikipedia search tool",
                description="Tool for searching wikipedia terms. Returns list of page ids matching tool input query that then can be retreived using WikipediaRetrieveTool",
                inputs=WikipediaSearchRequest,
                outputs=WikipediaSearchResponse,
                user_metadata={},
                demo_input=[WikipediaSearchRequest(
                    query="Python programming language"
                ), WikipediaSearchRequest(
                    query="Washington state"
                )]
                            
                    
            )

        async def run(self, inputs: WikipediaSearchRequest) -> WikipediaSearchResponse:
            search_results = wikipedia.search(inputs.query)
            if not search_results:
                return WikipediaSearchResponse(success=False, search_results=None)
            
            return WikipediaSearchResponse(success=True, search_results=search_results)
        
        
class WikipediaRetrieveRequest(BaseModel):
    query: str

class WikipediaRetrieveResponse(BaseModel):
    success: bool
    page_content: str


class WikipediaRetrieveTool(Tool):
        @property
        def card(self) -> ToolCard:
            return ToolCard(
                tool_id="WikipediaRetrieveTool",
                name="Wikipedia retrieve tool",
                description="Tool for retrieving wikipedia page content. Returns the content of the wikipedia page requested.",
                inputs=WikipediaRetrieveRequest,
                outputs=WikipediaRetrieveResponse,
                user_metadata={},
                demo_input=[WikipediaRetrieveRequest(
                    query="Python"
                ), WikipediaRetrieveRequest(
                    query="Washington"
                )]
                            
                    
            )

        async def run(self, inputs: WikipediaRetrieveRequest) -> WikipediaRetrieveResponse:
            page_content = wikipedia.page(inputs.query, auto_suggest=False).content
            return WikipediaRetrieveResponse(success=True, page_content=page_content)
