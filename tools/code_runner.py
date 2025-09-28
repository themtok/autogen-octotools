



import io
from typing import Optional
from pydantic import BaseModel, Field
from autogen_core import CancellationToken
from autogen_core.code_executor import CodeBlock
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor

from otools_autogen.tools import Tool, ToolCard
from pathlib import Path



class PythonCodeRunnerRequest(BaseModel):
    code: str = Field(..., description="""Python code to be executed in the Docker container.""")

class PythonCodeRunnerResponse(BaseModel):
    success: bool = Field(None, description="If the code execution was successful")
    response: Optional[str] = Field(None, description="Response from the code execution")
    error: str = Field(None, description="Error message if the code execution failed")


tool_card = ToolCard(
    tool_id="PythonCodeRunnerTool",
    name="Python Code Runner Tool",
    description="""Tool for executing Python code in a Docker container. Docker container has pre-installed libraries: fastapi, pydantic, openai, pandas
    Passed code should be a valid python code snippet. Code is executed in a secure isolated environment.""",
    inputs=PythonCodeRunnerRequest,
    outputs=PythonCodeRunnerResponse,
    user_metadata={},
    demo_input=[
        PythonCodeRunnerRequest(
            code="print('Hello, World!')"
        ),
        PythonCodeRunnerRequest(
            code="import pandas as pd; df = pd.DataFrame({'a': [1, 2, 3]}); df"
        )
    ]
)




class PythonCodeRunnerTool(Tool):
    @property
    def card(self) -> ToolCard:
        return tool_card

    async def run(self, inputs: PythonCodeRunnerRequest) -> PythonCodeRunnerResponse:
        work_dir = Path("coding")
        work_dir.mkdir(exist_ok=True)
        async with DockerCommandLineCodeExecutor(work_dir=work_dir, image="base-python:libs") as executor:  # type: ignore
            result = await executor.execute_code_blocks(
            code_blocks=[
                CodeBlock(language="python", code=inputs.code),

            ],
            cancellation_token=CancellationToken(),
        )
        return PythonCodeRunnerResponse(success=result.exit_code==0, response=result.output, error=result.output if result.exit_code!=0 else None)
        
