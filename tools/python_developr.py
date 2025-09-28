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




class PythonDeveloperRequest(BaseModel):
    program_description: str = Field(..., description="""Description of the program to be developed in Python. Should be a clear and concise description of the desired functionality.""")

class PythonDeveloperResponse(BaseModel):
    success: bool = Field(None, description="If request was successful")
    code: Optional[str] = Field(None, description="Generated Python code")
    error: str = Field(None, description="Error message if the code generation failed")


tool_card = ToolCard(
    tool_id="PythonDeveloperTool",
    name="Python Developer Tool",
    description="""Tool for creating Python programs based on a given description. Description should be clear and concise about the desired functionality of the program.
    Input data should be provided as part of the program description if needed. The generated code can then be executed using the Python Code Runner Tool.
    Returns the generated Python code as a string.""",
    inputs=PythonDeveloperRequest,
    outputs=PythonDeveloperResponse,
    user_metadata={},
    demo_input=[
        PythonDeveloperRequest(
            program_description="A Python program that prints 'Hello, World!' to the console."
        ),
        PythonDeveloperRequest(
            program_description="""A python program creates dataframe from below CSV string and plots average and median score by hour of day for each timezone in the data. Saves the plots as PNG files. CSV string is as follows:
            \"tz,hour,n_posts,avg_score,median_score,p25_score,p75_score\nAmerica/Los_Angeles,0,11966,12.997342477496787,2,1,4\nAmerica/Los_Angeles,1,13002,12.647383789756134,2,1,3\nAmerica/Los_Angeles,2,13423,11.935269899359561,2,1,3\nAmerica/Los_Angeles,3,13836,11.43258018815328,2,1,3\nAmerica/Los_Angeles,4,14038,10.911769634471634,2,1,3\nAmerica/Los_Angeles,5,14235,10.537907801414157,2,1,3\nAmerica/Los_Angeles,6,14524,10.426678603682847,2,1,3\nAmerica/Los_Angeles,7,15026,10.70582149023649,2,1,3\nAmerica/Los_Angeles,8,15576,11.353653846153847,2,1,4\nAmerica/Los_Angeles,9,16092,12.20498128342246,3,1,4\nAmerica/Los_Angeles,10,16536,13.330434782608695,3,1,5\nAmerica/Los_Angeles,11,16936,14.5523255813953495,,"""
            
        )
    ]
)


llm_logger = logging.getLogger("otools_autogen_llm")


class PythonDeveloperTool(Tool):
    @property
    def card(self) -> ToolCard:
        return tool_card

    async def run(self, inputs: PythonDeveloperRequest) -> PythonDeveloperResponse:
        client = AsyncOpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url=os.getenv("OPENROUTER_BASE_PATH"))
        persona_prompt  = f"Act as a python developer."
        prompt = f"""Write a python program based on the following description. Ensure the code is syntactically correct and can be executed in a python environment. 
        Output only the code without any explanation or additional text.
        Description: {inputs.program_description}"""
        input=[
            {"role": "developer","content": [{"type": "text", "text": persona_prompt}]},
            {"role": "user","content": [{"type": "text", "text": prompt}]}
            ]
        completion = await client.chat.completions.create(
            model="gpt-5-codex",
            messages=input)
        llm_response = completion.choices[0].message.content
        
        llm_logger.debug(f"[PythonCodeRunnerTool] LLM response: {llm_response}")
        return PythonDeveloperResponse.model_validate({
            "success": True,
            "code": llm_response
        })
