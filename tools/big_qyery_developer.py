import io
from typing import Optional
from pydantic import BaseModel, Field
from autogen_core import CancellationToken
from autogen_core.code_executor import CodeBlock
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor

from otools_autogen.tools import Tool, ToolCard
from pathlib import Path
from openai import AsyncOpenAI
import os
import logging




class BQDevRequest(BaseModel):
    query_description: str = Field(..., description="""Description of the query to be created in BigQuery. Should be a clear and concise description of the desired functionality.
                                     Must include DDL of the tables to be queried if needed.
                                     """)

class BQDevResponse(BaseModel):
    success: bool = Field(None, description="If request was successful")
    code: Optional[str] = Field(None, description="Generated BigQuery SQL")
    error: str = Field(None, description="Error message if the SQL generation failed")


tool_card = ToolCard(
    tool_id="BigQueryDeveloperTool",
    name="BigQuery Developer Tool",
    description="""Tool for creating BigQuery SQL queries based on a given description. Description should be clear and concise about the desired functionality of the query.
    Input data should be provided as part of the query description if needed. The generated SQL can then be executed using the BigQuery Runner Tool.
    Input of tool must include the DDL of the tables to be queried if needed.
    Returns the generated BigQuery SQL as a string.""",
    inputs=BQDevRequest,
    outputs=BQDevResponse,
    user_metadata={},
    demo_input=[
        BQDevRequest(
            program_description="""A BigQuery SQL query that selects all users from the users dataset. Dataset is named `project.dataset.users` and its DDL is as follows:
            CREATE TABLE `project.dataset.users` (
              `user_id` INT64,
              `user_name` STRING,
              `email` STRING,
              `created_at` TIMESTAMP
            );
            """
        ),
        BQDevRequest(
            program_description=""""A BigQuery SQL query that retrieves the top 5 countries by total sales from the sales dataset. Dataset is named `project.dataset.sales
            And its DDL is as follows:
            CREATE TABLE `project.dataset.sales` (
              `sale_id` INT64,
              `product_id` INT64,
              `country` STRING,
              `sale_amount` FLOAT64,
              `sale_date` DATE
            );
            """
            
        )
    ]
)


llm_logger = logging.getLogger("otools_autogen_llm")


class BigQueryDeveloperTool(Tool):
    @property
    def card(self) -> ToolCard:
        return tool_card

    async def run(self, inputs: BQDevRequest) -> BQDevResponse:
        client = AsyncOpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url=os.getenv("OPENROUTER_BASE_PATH"))
        persona_prompt  = f"Act as a BigQuery developer."
        prompt = f"""Write a BigQuery SQL query based on the following description. Ensure the query is syntactically correct and can be executed in a BigQuery environment. 
        Output only the query without any explanation or additional text.
        Description: {inputs.query_description}"""
        input=[
            {"role": "developer","content": [{"type": "text", "text": persona_prompt}]},
            {"role": "user","content": [{"type": "text", "text": prompt}]}
            ]
        response = client.responses.create(
            model="gpt-5-codex",
            input=prompt
        )
        response_output_message = [x for x in response.output if x.type == "message"]
        llm_response = response_output_message[0].content[0].text
        llm_logger.debug(f"[BigQueryDeveloperTool] LLM response: {llm_response}")
        return BQDevResponse.model_validate({
            "success": True,
            "code": llm_response
        })
