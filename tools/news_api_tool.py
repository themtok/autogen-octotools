from pydantic import BaseModel, Field
from otools_autogen.tools import Tool, ToolCard
import json
import requests
   
from datetime import datetime, timedelta
from typing import Optional


class NewsAPIToollRequest(BaseModel):
    sections: list[str] = Field(None, description="sections to fetch news from, aviailable sections: general , science , sports , business , health , entertainment , tech , politics , food , travel")
    search_term: Optional[str] = Field(None, description="Search term to filter news articles")
    max_results: Optional[int] = Field(3, description="Maximum number of search results to return")
    days_lookback: Optional[int] = Field(7, description="Number of days to look back for news articles")
    
class NewsAPIToolItem(BaseModel):
    title: str= Field(None, description="article title")
    link: str= Field(None, description="article URL")
    source: str   = Field(None, description="name of news source" )
    snippet: Optional[str]= Field(None, description="short description of the article")
    
class NewsAPIToolResponse(BaseModel):
    success: bool
    search_results: dict[str, list[NewsAPIToolItem]]= Field(None, description="news feed items")
    
        
tool_card=  ToolCard(
                tool_id="NewsAPITool",
                name="Nwes API Tool",
                description="Tool for fetch available News such as World, Sports, and Science",
                inputs=NewsAPIToollRequest,
                outputs=NewsAPIToolResponse,
                user_metadata={
                    "limitations": "This tool can use topics as follows: general , science , sports , business , health , entertainment , tech , politics , food , travel"},
                demo_input=[NewsAPIToollRequest(
                    sections= ['business']
                ), NewsAPIToollRequest(
                    sections= ['business', 'health', 'food', 'tech']
                )])


class NewsAPITool(Tool):
    @property
    def card(self) -> ToolCard:
        return tool_card
    
    def get_published_after_string(self, lookback: int) -> str:
        past_date = datetime.today() - timedelta(days=lookback)
        return past_date.strftime('%Y-%m-%d')
    
    
    async def run(self, inputs: NewsAPIToollRequest) -> NewsAPIToolResponse:
        
        url = 'https://api.thenewsapi.com/v1/news/all'
        params = {
            'api_token': 'NDdryV3JDzyb19TncCVWIgHbUUNHPEQ0zqDugEKF',
            'categories': ','.join(inputs.sections),
            'limit': inputs.max_results,
            'language': 'en',
        }
        if inputs.days_lookback:
            params['published_after'] = self.get_published_after_string(inputs.days_lookback)
        if inputs.search_term:
            params['search'] = inputs.search_term            

        response = requests.get(url, params=params)


        data = response.json()

        items = data.get('data', [])
        results = []
        for item in items:
            results.append(NewsAPIToolItem(
                title=item.get('title'),
                link=item.get('url'),
                og=item.get('image_url'),
                source=item.get('source'),
                snippet=item.get('snippet')
            ))
        r = {
            "success": True,
            "search_results": {
                inputs.sections[0]: results
            }
        }
        return NewsAPIToolResponse.model_validate(r)
       
    
    
if __name__ == "__main__":
    import asyncio
    async def f():
        t= NewsAPITool()
        print(await t.run(NewsAPIToollRequest(sections=["business"], search_term="Apple", max_results=5, days_lookback=7)))
    asyncio.run(f())