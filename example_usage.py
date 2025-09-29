import asyncio
from otools_autogen.runtime import Runtime, UserRequest, UserResponse
from colorama import Fore, Back, Style
from tools.wikipedia_search_tool import WikipediaSearch
from otools_autogen.runtime import UserRequest, UserResponse
from tools.search_engine_tool import SearchEngineTool
from tools.page_content_extractor import PageContentExtractionTool
from tools.generalist import GeneralistTool
from tools.api_caller_tool import APICallerTool
from tools.news_api_tool import NewsAPITool
from tools.critic_tool import CriticTool
from tools.code_runner import PythonCodeRunnerTool
from tools.hacker_news_bq import HackerNewsBigQueryCallerTool
from tools.python_developr import PythonDeveloperTool
from tools.big_qyery_developer import BigQueryDeveloperTool
from dotenv import load_dotenv
import os

load_dotenv()


async def m():
        runtime = Runtime()

        runtime.register_tool("HackerNewsBigQueryCallerTool", HackerNewsBigQueryCallerTool)
        runtime.register_tool("PythonCodeRunnerTool", PythonCodeRunnerTool)
        runtime.register_tool("GeneralistTool", GeneralistTool)
        runtime.register_tool("CriticTool", CriticTool)
        runtime.register_tool("PythonDeveloperTool", PythonDeveloperTool)
        runtime.register_tool("BigQueryDeveloperTool", BigQueryDeveloperTool)
        
        
        await runtime.start()
        sid = await runtime.send_message(UserRequest(message="What is the optimal hour to post on Hacker News to get the most upvotes?",
                                               files=[],
                                               max_steps=10))
        async for msg in runtime.stream(sid):
            mm:UserResponse = msg
            print(Fore.GREEN + f"===================================" + Style.RESET_ALL)
            print(Fore.GREEN + f"Type: {mm.type}" + Style.RESET_ALL)
            print(Fore.GREEN + f"Message: {mm.message}" + Style.RESET_ALL)
            print(Fore.BLUE + f"Tool_used: {mm.tool_used}" + Style.RESET_ALL)
            print(Fore.RED + f"Tool command: {mm.command}" + Style.RESET_ALL)
            print(Fore.RED + f"Current Step#: {mm.step_no}" + Style.RESET_ALL)
            print(Fore.RED + f"Conclusion: {mm.conclusion}" + Style.RESET_ALL)
            print(Fore.RED + f"Final: {mm.final}" + Style.RESET_ALL)
            print(Fore.GREEN + f"===================================" + Style.RESET_ALL)

        
        await runtime.stop(True)



if __name__ == "__main__":
    asyncio.run(m())
