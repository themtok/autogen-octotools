from abc import ABC, abstractmethod
from dataclasses import dataclass
from pydantic import BaseModel
from autogen_core import BaseAgent, MessageContext
from .utils import only_direct
import logging

logger = logging.getLogger("otools_autogen")

@dataclass
class ToolCard:
    """
    Represents a tool card with metadata and schema information.
    Attributes:
        tool_id (str): A unique identifier for the tool.
        name (str): The name of the tool.
        description (str): A brief description of the tool.
        demo_input (list): Example input data for demonstration purposes.
        inputs (type[BaseModel]): The input data model type, derived from BaseModel.
        outputs (type[BaseModel]): The output data model type, derived from BaseModel.
        user_metadata (dict): Additional metadata provided by the user.
    Methods:
        get_metadata():
            Returns a dictionary containing metadata about the tool, including
            its ID, name, description, input/output schemas, user metadata, 
            and demo input.
    """
    tool_id: str
    name: str
    description: str
    demo_input: list
    inputs: type[BaseModel]
    outputs: type[BaseModel]
    user_metadata: dict

    def get_metadata(self):
        return {
            "tool_id": self.tool_id,
            "tool_name": self.name,
            "tool_description": self.description,
            "input_type_json_schema": self.inputs.model_json_schema(),
            "output_type_json_schema": self.outputs.model_json_schema(),
            "user_metadata": self.user_metadata,
            "demo_input": self.demo_input,
        }
    
    


class Tool(ABC):
    """
    Abstract base class representing a tool.
    This class serves as a blueprint for creating tools with a defined interface.
    Subclasses must implement the `card` property and the `run` method.
    Attributes:
        card (ToolCard): An abstract property that must be implemented to return
            a `ToolCard` instance representing the tool's metadata or configuration.
    Methods:
        run(inputs: BaseModel) -> BaseModel:
            An abstract asynchronous method that must be implemented to define
            the tool's execution logic. It takes an input of type `BaseModel` and
            returns an output of type `BaseModel`.
    """
    @property
    @abstractmethod
    def card(self) -> ToolCard:
        pass
    
    @abstractmethod
    async def run(self, inputs: BaseModel) -> BaseModel:
        pass
    
    
    
def create_tool_class(tool: Tool) -> type[BaseAgent]:
        """
        Dynamically creates a tool-specific agent class that inherits from `BaseAgent`.
        This function generates a new class with a custom `__init__` method and an
        asynchronous `on_message_impl` method. The generated class is tailored to
        handle messages and execute the logic defined in the provided `tool` object.
        Args:
            tool (Tool): An instance of the `Tool` class containing the tool's
                         configuration, including its card inputs, outputs, and
                         execution logic.
        Returns:
            type[BaseAgent]: A dynamically created class that inherits from `BaseAgent`
                             and implements the tool-specific behavior.
        """
        async def on_message_impl(self, message, ctx: MessageContext):
            parsed_message = None
            if isinstance(message, tool.card.inputs):
                parsed_message = message
            else:
                parsed_message = tool.card.inputs.model_validate(message)
            out = await tool.run(parsed_message) 
            parsed_response = tool.card.outputs.model_validate(out)                           
            return parsed_response

        on_message_impl.__annotations__ = {
            "message": tool.card.inputs,
            "ctx": MessageContext,
            "return": None,
        }

        on_message_impl = only_direct(on_message_impl)

        def __init__(self):
            logger.debug(f"Tool initialization {tool.card.name} agent. {str(self)}")
            super(self.__class__, self).__init__(f"Tool: {tool.card.name} agent.")

        class_dict = {
            "__init__": __init__,
            "on_message_impl": on_message_impl
        }

        ToolCls = type(tool.card.tool_id, (BaseAgent,), class_dict)

        return ToolCls