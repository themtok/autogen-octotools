from pydantic import BaseModel, Field
from otools_autogen.tools import Tool, ToolCard
from openai import AsyncOpenAI
import os
import logging

llm_logger = logging.getLogger("otools_autogen_llm")

class GeneralistToolRequest(BaseModel):
    prompt: str = Field(description=" The prompt that includes query from the user to guide the agent to generate response (Examples: 'Describe this image in detail')")
    persona_type: str = Field(None, description="Persona type that the agent should adopt (Examples: 'Expert', 'Generalist', 'Researcher')")
    
class GeneralistToolResponse(BaseModel):
    response: str= Field(None, description="The generated response to the original query prompt")
    
    
    
tool_card= ToolCard(
                tool_id="GeneralistTool",
                description="A generalized tool that takes query from the user as prompt, and answers the question step by step to the best of its ability.",
                name="Generalist Tool",
                inputs=GeneralistToolRequest,
                outputs=GeneralistToolResponse,
                user_metadata={
                     
                "limitation": "The GeneralistTool may provide hallucinated or incorrect responses.",
                "best_practice": "Use the GeneralistTool for general queries or tasks that don't require specialized knowledge or specific tools in the toolbox. For optimal results:\n\n"
                "1) Provide clear, specific prompts.\n"
                "2) Use it to answer the original query through step by step reasoning for tasks without complex or multi-step reasoning.\n"
                "3) For complex queries, break them down into subtasks and use the tool multiple times.\n"
                "4) Use it as a starting point for complex tasks, then refine with specialized tools.\n"
                "5) Verify important information from its responses.\n"
        
                    },
                demo_input=[
                    GeneralistToolRequest(prompt="Summarize given text in 3 sentences <TEXT>", persona_type="Generalist"),
                    GeneralistToolRequest(prompt="Extract most important financial information from text below <TEXT>", persona_type="Financial Expert")
                ])




class GeneralistTool(Tool):
    @property
    def card(self) -> ToolCard:
        return tool_card
    
    async def run(self, inputs: None) -> None:
        client = AsyncOpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url=os.getenv("OPENROUTER_BASE_PATH"))
        persona_prompt  = f"Act as a {inputs.persona_type}."
        input=[
            {"role": "developer","content": [{"type": "text", "text": persona_prompt}]},
            {"role": "user","content": [{"type": "text", "text": inputs.prompt}]}
            ]
        completion = await client.chat.completions.create(
            model=os.getenv("OTOOLS_MODEL"),
            messages=input)
        llm_response = completion.choices[0].message.content
        
        llm_logger.debug(f"[GeneralistTool] LLM response: {llm_response}")
        return GeneralistToolResponse.model_validate({
            "response": llm_response
        })

       