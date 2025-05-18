from pydantic import BaseModel, Field
from otools_autogen.tools import Tool, ToolCard
import trafilatura
from openai import AsyncOpenAI
import os
import logging

llm_logger = logging.getLogger("otools_autogen_llm")

class PageContentExtractionRequest(BaseModel):
    link: str = Field(None, description="Link to the page to extract content from")
    main_query: str = Field(None, description="Main query that should be used to extract and summarize the content from the page")
    
class PageContentExtractionResult(BaseModel):
    success: bool = Field(description="If page content extraction was successful this will be True")
    markdown_content: str= Field(None, description="Extracted content in markdown format")
    
    
tool_card= ToolCard(
                tool_id="PageContentExtractionTool",
                description="Tool for extracting content from the page. Returns summarized content. Summary is done using the main query provided. Accepts only one link at a time.",
                name="Page Content Extraction",
                inputs=PageContentExtractionRequest,
                outputs=PageContentExtractionResult,
                user_metadata={
                  "recommendation of usage of main_query": "The main query should be a single line and should be used to summarize the content of the page. If you don't want to use specific query, use main query provided by user.",  
                },
                demo_input=[
                    PageContentExtractionRequest(link="https://en.wikipedia.org/wiki/Python_(programming_language)", main_query="Python programming language"),
                    PageContentExtractionRequest(link="https://www.python.org/", main_query="List comprehension in python"),          
                ])

class PageContentExtractionTool(Tool):
    @property
    def card(self) -> ToolCard:
        return tool_card
    
    
    async def run(self, inputs: PageContentExtractionRequest) -> PageContentExtractionResult:
        import trafilatura
        downloaded = trafilatura.fetch_url(inputs.link)
        if downloaded is None:
            return PageContentExtractionResult.model_validate({
                "success": False,
                "markdown_content": None
            })
        r = trafilatura.extract(downloaded,output_format="markdown")
        if r is None:
            return PageContentExtractionResult.model_validate({
                "success": False,
                "markdown_content": None
            })
            
        prompt = f"""Summarize the content of the page in markdown format. Use the main query provided to summarize the content. The main query is: {inputs.main_query}. 
The content of the page is: {r}"""
        llm_logger.debug(f"[PageContentExtractionTool] LLM prompt: {prompt}")
        client = AsyncOpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url=os.getenv("OPENROUTER_BASE_PATH"))
        input=[{"role": "user","content": [{"type": "text", "text": prompt}]}]
        completion = await client.chat.completions.create(
            model=os.getenv("PAGE_CONTENT_EXTRACTOR_SUMMARIZATION_MODEL"),
            messages=input)
        llm_response = completion.choices[0].message.content
        llm_logger.debug(f"[PageContentExtractionTool] LLM response: {llm_response}")
        return PageContentExtractionResult.model_validate({
            "success": True,
            "markdown_content": r
        })
        
if __name__ == "__main__":
    async def m():
        tool = PageContentExtractionTool()
        r= await tool.run(PageContentExtractionRequest(link="https://news.google.com/read/CBMicEFVX3lxTFBtcUowRUt6QXZKRzZ4RktCcWlBcFRTbkVHSDFzWV94aG5NdFgxQVFmSVhCWHBSMXY4dWJaSFA3by0tb1dqcVZ3MWFIRDd0TWF3LXRaWWlndW0tZ1cwdVBpb3dIOTVEMk45Qk9XakVGRnA?hl=en-US&gl=US&ceid=US%3Aen"))
        print(r)
    import asyncio
    asyncio.run(m())
    
    