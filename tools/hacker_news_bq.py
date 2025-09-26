



import io
from typing import Optional
from pydantic import BaseModel, Field

from otools_autogen.tools import Tool, ToolCard


class HackerNewsBQRequest(BaseModel):
    sql_query: str = Field(..., description="""BigQuery query to be executed on the Hacker News dataset in BigQuery. Must be a SELECT query.
                           And it must be a select statement from the following table: `bigquery-public-data.hacker_news.full`
                           Must also have a LIMIT clause to limit the number of rows returned. Max limit is 1000 rows.""")

class HackerNewsBQResponse(BaseModel):
    success: bool = Field(None, description="If the API call was successful")
    response: Optional[str] = Field(None, description="Response from the API call in form of CSV string")
    error: str = Field(None, description="Error message if the API call failed")
 

tool_card = ToolCard(
    tool_id="HackerNewsBigQueryCallerTool",
    name="Hacker News BigQuery Caller Tool",
    description="""Tool for calling the Hacker News table in BigQuery. 
    This dataset contains all stories and comments from Hacker News from its launch in 2006.  Each story contains a story id, the author that made the post, when it was written, and the number of points the story received.
    DDL for the table is as follows:
    CREATE TABLE `bigquery-public-data.hacker_news.full`
(
  title STRING OPTIONS(description="Story title"),
  url STRING OPTIONS(description="Story url"),
  text STRING OPTIONS(description="Story or comment text"),
  `by` STRING OPTIONS(description="The username of the item's author."),
  score INT64 OPTIONS(description="Story score"),
  time INT64 OPTIONS(description="Unix time"),
  timestamp TIMESTAMP OPTIONS(description="Timestamp for the unix time"),
  type STRING OPTIONS(description="type of details (comment comment_ranking poll story job pollopt)"),
  id INT64 OPTIONS(description="The item's unique id."),
  parent INT64 OPTIONS(description="Parent comment ID"),
  descendants INT64 OPTIONS(description="Number of story or poll descendants"),
  ranking INT64 OPTIONS(description="Comment ranking"),
  deleted BOOL OPTIONS(description="Is deleted?")
)
OPTIONS(
  description="A full daily update of all the stories and comments in Hacker News."
);""",
    inputs=HackerNewsBQRequest,
    outputs=HackerNewsBQResponse,
    user_metadata={},
    demo_input=[
        HackerNewsBQRequest(
            sql_query="SELECT title, url, score, time FROM `bigquery-public-data.hacker_news.full` WHERE type='story' AND score > 1000 ORDER BY score DESC LIMIT 10"
        ),
        HackerNewsBQRequest(
            sql_query="SELECT `by`, COUNT(*) as num_posts FROM `bigquery-public-data.hacker_news.full` WHERE type='story' GROUP BY `by` ORDER BY num_posts DESC LIMIT 10"
        )
    ]
)



class HackerNewsBigQueryCallerTool(Tool):
    @property
    def card(self) -> ToolCard:
        return tool_card

    async def run(self, inputs: HackerNewsBQRequest) -> HackerNewsBQResponse:
        from google.cloud import bigquery
        from google.oauth2 import service_account
        import pandas as pd

        
        print(f"\n\n\n\nExecuting query:\n{inputs.sql_query}\n\n\n")
        try:
            
            client = bigquery.Client()

            query_job = client.query(inputs.sql_query)
            results = query_job.result()

            # Convert results to a pandas DataFrame and then to CSV string
            df = results.to_dataframe()
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)  # index=False to skip row numbers
            csv_string = csv_buffer.getvalue()
            print(f"\n\n\n\nQuery executed successfully. Number of rows returned: {len(df)}\n\n\n")

            return HackerNewsBQResponse(success=True, response=csv_string, error="")
        except Exception as e:
            return HackerNewsBQResponse(success=False, response=None, error=str(e))
