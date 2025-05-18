from otools_autogen.tools import Tool, ToolCard
from pydantic import BaseModel
import wikipedia



class WikipediaSearchRequest(BaseModel):
    query: str
    max_length_of_response:int=2000
    
class WikipediaSearchResponse(BaseModel):
    success: bool
    search_results: str
    

class WikipediaSearch(Tool):
        @property
        def card(self) -> ToolCard:
            return ToolCard(
                tool_id="WikipediaSearchTool",
                name="Wikipedia search tool",
                description="Tool for searching wikipedia.",
                inputs=WikipediaSearchRequest,
                outputs=WikipediaSearchResponse,
                user_metadata={},
                demo_input=[WikipediaSearchRequest(
                    query="Python"
                ), WikipediaSearchRequest(
                    query="Washington"
                )]
                            
                    
            )

        async def run(self, inputs: WikipediaSearchRequest) -> WikipediaSearchResponse:
            search_results = wikipedia.search(inputs.query)
            if not search_results:
                return WikipediaSearchResponse(success=False, search_results=None)
            page = wikipedia.page(search_results[0])
            text = page.content

            if inputs.max_length_of_response is not None:
                text = text[:inputs.max_length_of_response]
            return WikipediaSearchResponse(success=True, search_results=text)