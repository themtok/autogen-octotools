from dataclasses import dataclass
import asyncio
from functools import wraps

from autogen_core._default_subscription import DefaultSubscription
from autogen_core._default_topic import DefaultTopicId
import uuid
import enum
from typing import Any, Optional
from autogen_core import (SingleThreadedAgentRuntime)
from .tools import create_tool_class, Tool, ToolCard


from autogen_core import TRACE_LOGGER_NAME

from .agents import Orchestrator, QueryAnalyzer, ActionPredictor, CommandGenerator, ContextVerifier, FinalOutputAgent
import logging

logger = logging.getLogger("otools_autogen")



@dataclass
class UserRequest:
    """
    Represents a user request containing a message, a list of files, and an optional maximum number of steps.

    Attributes:
        message (str): The message provided by the user.
        files (list[str]): A list of file paths associated with the request.
        max_steps (int): The maximum number of steps allowed for processing the request. Defaults to 5.
    """
    message: str
    files: list[str]
    max_steps: int = 5

@dataclass
class UserResponse:
    """
    Represents a user's response during a session.

    Attributes:
        type (str): The type of the response.
        session_id (str): The unique identifier for the session.
        message (str): The message content of the response.
        tool_used (str): The name of the tool used in the response.
        final (bool): Indicates if this is the final response in the session.
        conclusion (bool): Indicates if the response contains a conclusion.
        step_no (int): The step number associated with the response.
        command (Optional[str]): An optional command associated with the response.
    """
    type: str
    session_id: str
    message: str
    tool_used: str
    final: bool
    conclusion: bool
    step_no: int
    command: Optional[str] = None


       
            


class Runtime:
    """
    The `Runtime` class is responsible for managing tools, sessions, and the runtime environment
    for an agent-based system. It provides methods to register tools, manage sessions, send messages,
    stream responses, and control the lifecycle of the runtime.
    Classes:
        - SessionState: An enumeration representing the state of a session (WAITING or PROCESSING).
        - Session: A dataclass representing a session with attributes for session ID, a queue for
          communication with the client, and the session state.
    Methods:
        - __init__(): Initializes the Runtime instance with empty tool and session registries.
        - register_tool(tool_name, tool): Registers a tool by its name and type.
        - get_tool(tool_name): Retrieves a registered tool by its name.
        - get_session(session_id): Retrieves a session by its ID.
        - get_tool_cards(): Returns a dictionary of tool names and their associated cards.
        - _init_session(session_id): Initializes a new session with a unique ID and sets its state
          to WAITING. Publishes a bootstrap message to the runtime.
        - send_message(message, session_id): Sends a user request message to the runtime. If the
          session does not exist, it initializes a new session.
        - stream(session_id): Streams messages from the session's queue to the client. Stops when
          a final message is received.
        - start(): Starts the runtime by initializing internal agents, registering tools, and
          adding subscriptions.
        - stop(when_idle): Stops the runtime. If `when_idle` is True, the runtime stops when idle.
        - _add_internal_agents(runtime): Adds internal agents to the runtime, such as QueryAnalyzer,
          ActionPredictor, CommandGenerator, ContextVerifier, FinalOutputAgent, and Orchestrator.
    """
    
    class SessionState(enum.Enum):
        """
        SessionState is an enumeration that represents the state of a session.

        Attributes:
            WAITING (int): Indicates that the session is in a waiting state.
            PROCESSING (int): Indicates that the session is currently being processed.
        """
        WAITING = 1
        PROCESSING = 2
    
    @dataclass
    class Session:
        """
        Represents a session within the runtime.

        Attributes:
            session_id (str): A unique identifier for the session.
            to_client_queue (asyncio.Queue): A queue used for sending messages to the client.
            state (Runtime.SessionState): The current state of the session.
        """
        session_id: str
        to_client_queue: asyncio.Queue
        state: "Runtime.SessionState"
        
        
    def __init__(self):
        """
        Initializes the runtime environment.

        This constructor sets up the necessary data structures for managing tools
        and sessions. It initializes two dictionaries:
        - `_tools`: A dictionary to store tool-related information.
        - `_sessions`: A dictionary to manage session-related data.
        """
        self._tools = {}
        self._sessions = {}
        
    def register_tool(self, tool_name,tool: type[Tool]):
        """
        Registers a tool with the given name and type.

        Args:
            tool_name (str): The name to associate with the tool.
            tool (type[Tool]): The class type of the tool to be registered. 
                               An instance of this class will be created and stored.

        Returns:
            None
        """
        self._tools[tool_name] = tool()
    
    def get_tool(self, tool_name: str) -> Tool:
        """
        Retrieve a tool instance by its name.

        Args:
            tool_name (str): The name of the tool to retrieve.

        Returns:
            Tool: The tool instance associated with the given name.

        Raises:
            KeyError: If the tool name does not exist in the collection.
        """
        return self._tools[tool_name]
    
    def get_session(self, session_id: str) -> "Runtime.Session":
        """
        Retrieve a session by its session ID.

        Args:
            session_id (str): The unique identifier of the session to retrieve.

        Returns:
            Runtime.Session: The session object associated with the given session ID.

        Raises:
            KeyError: If the session ID does not exist in the session dictionary.
        """
        return self._sessions[session_id]
    
    def get_tool_cards(self) -> dict:
        """
        Retrieve a dictionary of tool cards.

        This method returns a dictionary where the keys are tool names and the 
        values are the corresponding tool card objects.

        Returns:
            dict: A dictionary mapping tool names (str) to their respective 
            tool card objects.
        """
        return {tool_name: tool.card for tool_name, tool in self._tools.items()}

    async def  _init_session(self, session_id: str):
        """
        Initialize a new session or raise an error if the session ID already exists.

        Args:
            session_id (str): The unique identifier for the session. If None, a new UUID will be generated.

        Returns:
            str: The session ID of the newly created session.

        Raises:
            ValueError: If a session with the given session ID already exists.

        Notes:
            - A new session is added to the `_sessions` dictionary with the specified or generated session ID.
            - A message with the topic "bootstrap" is published to the runtime with the session ID as the source.
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        else:
            if session_id in self._sessions:
                raise ValueError(f"Session with id {session_id} already exists.")
        self._sessions[session_id] = Runtime.Session(
            session_id=session_id,
            to_client_queue=asyncio.Queue(),
            state=Runtime.SessionState.WAITING
        )
        await self.runtime.publish_message("bootstrap", DefaultTopicId(source=session_id))   
        return session_id

        
        

    async def send_message(self, message: UserRequest, session_id: str = None):
        """
        Sends a message to the runtime and associates it with a session.

        If the provided session ID does not exist in the current sessions, a new session
        will be initialized. The message is then published to the runtime under the
        specified session's topic.

        Args:
            message (UserRequest): The message to be sent.
            session_id (str, optional): The ID of the session to associate with the message.
                If not provided or if the session ID does not exist, a new session will be created.

        Returns:
            str: The session ID associated with the message.
        """
        if session_id not in self._sessions:
            session_id = await self._init_session(session_id)
        _session = self._sessions[session_id]
        await self.runtime.publish_message(message=message,topic_id=DefaultTopicId(source=session_id))
        return session_id
    
    async def stream(self, session_id):
        """
        Asynchronous generator that streams messages from a session's client queue.
        Args:
            session_id (str): The unique identifier for the session.
        Yields:
            UserResponse: A message object retrieved from the session's client queue.
        Raises:
            RuntimeError: If the provided session_id is not valid or does not exist.
        Behavior:
            - Continuously retrieves messages from the session's `to_client_queue`.
            - Yields each message to the caller.
            - Terminates the stream when a message with the `final` attribute set to True is encountered.
        """
        if session_id not in self._sessions:
            raise RuntimeError("Invalid session")

        queue = self._sessions[session_id].to_client_queue

        while True:
            msg:UserResponse = await queue.get()
            yield msg
            if msg.final:
                break

    async def start(self):
        """
        Asynchronously starts the runtime and initializes tools and subscriptions.
        This method performs the following steps:
        1. Creates an instance of `SingleThreadedAgentRuntime` and assigns it to `self.runtime`.
        2. Adds internal agents to the runtime by calling `_add_internal_agents`.
        3. Iterates over the tools in `self._tools`, creates tool classes using `create_tool_class`,
           and registers them with the runtime.
        4. Creates a default subscription for each tool and adds it to the runtime.
        5. Starts the runtime.
        Raises:
            Any exceptions raised during the initialization or runtime start process.
        """
        self.runtime = SingleThreadedAgentRuntime()
        await self._add_internal_agents(self.runtime)
        for tool_id, tool in self._tools.items():
            tool_cls = create_tool_class(tool)
            await tool_cls.register(
                runtime=self.runtime,
                type=tool_id,
                factory=lambda cls=tool_cls: cls()
            )
            subscr = DefaultSubscription(agent_type=tool_id)
            await self.runtime.add_subscription(subscr)
        
        
        self.runtime.start()
         

    async def stop(self,when_idle=False):
        """
        Stops the runtime either immediately or when it becomes idle.

        Args:
            when_idle (bool, optional): If True, the runtime will stop when it becomes idle.
                                        If False, the runtime will stop immediately. Defaults to False.

        Raises:
            Any exceptions raised by the `stop_when_idle` or `stop` methods of the runtime.
        """
        if when_idle:
            await self.runtime.stop_when_idle()
        else:
            await self.runtime.stop()


    async def _add_internal_agents(self, runtime):
        """
        Asynchronously adds internal agents and their subscriptions to the runtime.
        This method registers a predefined set of internal agents with the runtime,
        creates default subscriptions for each agent, and adds these subscriptions
        to the runtime. Additionally, it registers and subscribes an Orchestrator
        agent.
        Args:
            runtime: The runtime instance to which the agents and subscriptions
                     will be added.
        Agents Registered:
            - QueryAnalyzer
            - ActionPredictor
            - CommandGenerator
            - ContextVerifier
            - FinalOutputAgent
            - OrchestratorAgent
        Each agent is registered with a factory function that creates an instance
        of the respective agent class. A `DefaultSubscription` is created for each
        registered agent type and added to the runtime.
        Note:
            The Orchestrator agent is registered separately after the internal
            agents and uses a factory function that passes `self` to its
            constructor.
        """
        internal_agents = [
            ("QueryAnalyzer", QueryAnalyzer),
            ("ActionPredictor", ActionPredictor),
            ("CommandGenerator", CommandGenerator),
            ("ContextVerifier", ContextVerifier),
            ("FinalOutputAgent", FinalOutputAgent),
        ]
        
        for agent_name, agent_cls in internal_agents:
            agent_type = await agent_cls.register(
                runtime=runtime,
                type=agent_name,
                factory=lambda cls=agent_cls: cls()
            )
            subscr = DefaultSubscription(agent_type=agent_type)
            await runtime.add_subscription(subscr)
            
            
        
        from .agents import Orchestrator
        orch_agent_type = await Orchestrator.register(
            runtime=runtime,
            type="OrchestratorAgent",
            factory=lambda: Orchestrator(self)
        )
        
        orch_subscr = DefaultSubscription(agent_type=orch_agent_type)
        await runtime.add_subscription(orch_subscr)
       

        