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
from dotenv import load_dotenv

load_dotenv()


async def m():
        runtime = Runtime()
        
        runtime.register_tool("WikipediaSearchTool", WikipediaSearch)
        runtime.register_tool("SearchEngineTool", SearchEngineTool)
        runtime.register_tool("PageContentExtractionTool", PageContentExtractionTool)
        runtime.register_tool("NewsAPITool", NewsAPITool)
        runtime.register_tool("GeneralistTool", GeneralistTool)
        runtime.register_tool("APICallerTool", APICallerTool)
        runtime.register_tool("CriticTool", CriticTool)
        
        await runtime.start()
        sid = await runtime.send_message(UserRequest(message="Describe picture",
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
