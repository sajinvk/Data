# **MCP Client**
MCP is a protocol where an MCP client connects to an MCP server. The server exposes capabilities such as tools, and the client can discover and call them. 
In your code, Claude is not the MCP client. Your Python program (MCP_ChatBot) is the MCP client. Claude is the LLM that decides which tool to use, while your Python code actually connects to the MCP server and performs the tool call through the MCP session.

## Architecture
* The user typing a question in the console. [modelconte...tocol.info]
* Claude, which reads the question and decides whether a tool is needed via the Messages API. Anthropic describes the Messages API as the direct model-access interface where you manage the conversation and tool loop yourself. [platform.claude.com], [platform.claude.com]
* An MCP server, which exposes tools that your client can discover with list_tools() and invoke with call_tool().

