from pydantic import BaseModel, Field
from otools_autogen.tools import Tool, ToolCard
from openai import AsyncOpenAI
import os
import logging

llm_logger = logging.getLogger("otools_autogen_llm")

class CriticToolRequest(BaseModel):
    information_set: str = Field(description="Complete Information set that should be validated by critic tool ")
    
class CriticToolResponse(BaseModel):
    feedback: str= Field(None, description="Feedback from the critic tool about the information set")
    
    
    
tool_card= ToolCard(
                tool_id="CriticTool",
                description="Critic tool that takes information set as input and validates it in terms of comprehensiveness, correctness and relevance. It provides feedback about the information set.",
                name="Critic Tool",
                inputs=CriticToolRequest,
                outputs=CriticToolResponse,
                user_metadata={
                     
                "limitation": "The CriticTool may provide hallucinated or incorrect responses.",
                "recommendation of usage": "The CriticTool should be used to validate the information set in terms of comprehensiveness, correctness and relevance if you are not sure about the information set. It is not recommended to use the CriticTool for generating new information or for validating information that is already known to be correct.",

        
                    },
                demo_input=[
                    CriticToolRequest(information_set="Assess the following information set: <TEXT>"),
                    CriticToolRequest(information_set="Check the following information set for correctness and relevance: <TEXT>")
                ])




class CriticTool(Tool):
    @property
    def card(self) -> ToolCard:
        return tool_card
    
    async def run(self, inputs: None) -> None:
        client = AsyncOpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url=os.getenv("OPENROUTER_BASE_PATH"))
        persona_prompt  = f"Act as a Critic of infomation you receive. Be demanding and strict, but not excessively."
        prompt = f"Validate the following information set in terms of comprehensiveness, correctness and relevance. Provide feedback about the information set. "
        prompt += f"Information set: {inputs.information_set}"
        
        input=[
            {"role": "developer","content": [{"type": "text", "text": persona_prompt}]},
            {"role": "user","content": [{"type": "text", "text": prompt}]}
            ]
        completion = await client.chat.completions.create(
            model=os.getenv("OTOOLS_MODEL"),
            messages=input)
        llm_response = completion.choices[0].message.content
        
        llm_logger.debug(f"[CriticTool] LLM response: {llm_response}")
        return CriticToolResponse.model_validate({
            "feedback": llm_response
        })

       