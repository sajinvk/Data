# **MCP Client**
MCP is a protocol where an MCP client connects to an MCP server. The server exposes capabilities such as tools, and the client can discover and call them. 
In your code, Claude is not the MCP client. Your Python program (MCP_ChatBot) is the MCP client. Claude is the LLM that decides which tool to use, while your Python code actually connects to the MCP server and performs the tool call through the MCP session.

## Architecture
* The user typing a question in the console. 
* Claude, which reads the question and decides whether a tool is needed via the Messages API. Anthropic describes the Messages API as the direct model-access interface where you manage the conversation and tool loop yourself.
* An MCP server, which exposes tools that your client can discover with list_tools() and invoke with call_tool().

## MCP lets a chatbot use external tools through servers. 
 Ref: https://github.com/modelcontextprotocol 

* Think of the chatbot as a brain/coordinator, and MCP servers as specialized helpers.
* Instead of hardcoding those helpers in code, you can define them in a config file like server_config.json.
* The JSON file is like a setup sheet that tells the chatbot:
    what servers exist
    how to start them
    what tools are available
* Server configuration example 
### Analogy 

Think of it like a building directory:

The whole JSON = the building
The servers section = list of offices in the building
Each server name = one office
Inside each server:

command = how to open the office
args = extra instructions
other fields = rules/settings for that office

```json
{
  "servers": {
    "serverA": {
      "command": "some-command",
      "args": ["arg1", "arg2"],
      "env": {
        "KEY": "value"
      },
      "cwd": "./folder",
      "enabled": true
    },
    "serverB": {
      "command": "another-command",
      "args": ["arg1"]
    }
  }
} 
```
# Understanding Multiple MCP Server Connections

When moving from a chatbot that connects to **one MCP server** to a chatbot that connects to **multiple MCP servers**, a few new concepts are introduced.

The goal is simple:

- connect to multiple servers
- keep track of which tools come from which server
- send tool calls to the correct server
- clean up all connections properly when done

---

## Big Picture

Earlier, the chatbot had:

- **one server**
- **one session**

Now, the chatbot can connect to:

- **many servers**
- **one separate session for each server**

A simple way to think about it:

> The chatbot is like a manager calling multiple departments.  
> Each department has its own phone line.  
> The manager also keeps a directory to know which department handles which task.

---

## 1. List of Client Sessions

Instead of storing just one session, the chatbot now stores a **list of client sessions**.

### What this means

- each session is a **1-to-1 connection**
- one session connects to **one MCP server**
- if you have 3 servers, you will have 3 sessions

### Easy way to remember

> **One server = one conversation line**

So the chatbot keeps multiple conversation lines open, one for each server.

---

## 2. `available_tools`

`available_tools` is the combined list of all tools exposed by all connected servers.

### What this means

Each MCP server may provide its own tools.

For example:

- a filesystem server may provide file tools
- a fetch server may provide web tools
- a research server may provide research tools

The chatbot needs one master list of all tools it can use.

### Easy way to remember

> **`available_tools` = master tool menu**

This is the full menu of tools that the chatbot can choose from.

---

## 3. `tool_to_session`

`tool_to_session` is a mapping between a tool name and the session that should be used to call that tool.

### Why this is needed

When the LLM decides to use a tool, it only gives the **tool name**.

Example:

- the LLM says: use `read_file`

Your code then needs to answer:

- which server owns `read_file`?
- which session is connected to that server?

That is what `tool_to_session` helps with.

### Easy way to remember

> **`tool_to_session` = routing table**

It tells your program where to send the request.

### Example idea

- `read_file` -> filesystem session
- `fetch_url` -> fetch session
- `search_papers` -> research session

So when a tool is chosen, your program knows which session to use.

---

## 4. `exit_stack`

`exit_stack` is used to manage all the MCP clients and sessions so they can be properly closed later.

### Why it is needed

In Lesson 5, you used the `with` statement, which automatically cleaned up resources for you.

That worked well when you had a small fixed number of resources.

But now, the number of servers may vary depending on the configuration file.

If you used `with` statements directly, you might end up with many nested `with` blocks.

`exit_stack` solves that problem by letting you dynamically add resources as you create them.

### Easy way to remember

> **`exit_stack` = cleanup manager**

It keeps track of everything you opened so it can all be closed safely later.

### Another analogy

> It is like placing all opened resources onto a tray so you can put them away neatly when finished.

---

## 5. `connect_to_servers`

`connect_to_servers` is the method that reads the server configuration file and connects to all listed servers.

### What it does

- reads the JSON configuration file
- finds all the server entries
- loops through them one by one
- calls `connect_to_server` for each server

### Easy way to remember

> **`connect_to_servers` = setup everything from config**

It handles the overall setup for all servers.

---

## 6. `connect_to_server`

`connect_to_server` is a helper method that handles the connection to one server.

### What it does

For a single server, it:

1. creates an MCP client
2. launches the server as a subprocess
3. creates a client session
4. connects to the server
5. gets the list of tools exposed by that server

### Easy way to remember

- `connect_to_servers` = connect to all servers
- `connect_to_server` = connect to one server

---

## 7. `cleanup`

`cleanup` is a helper method that shuts everything down properly when the chatbot is done.

### Why it matters

When working with multiple connections, you do not want to leave:

- sessions open
- subprocesses running
- resources hanging around

That can lead to **resource leaks**, especially in networked applications.

### How it works

It closes resources stored in `exit_stack` in the **reverse order** they were added.

### Easy way to remember

> **Like stacking and unstacking plates**  
> The last plate placed on the stack is the first one removed.

That is why cleanup happens in reverse order.

---

## Simple Analogy

Think of the chatbot as a **call center operator**.

### In this analogy

- **servers** = departments
- **sessions** = phone lines
- **available_tools** = service catalog
- **tool_to_session** = department directory
- **exit_stack** = desk organizer for active calls
- **connect_to_servers** = startup routine that dials all departments
- **connect_to_server** = dial one department
- **cleanup** = end-of-day routine that hangs up every call properly

This makes the whole system much easier to understand.

---

## Short Summary

When using multiple MCP servers:

- you need **one session per server**
- you collect all tools into **`available_tools`**
- you map each tool to its correct session using **`tool_to_session`**
- you manage resources safely using **`exit_stack`**
- you connect to all servers using **`connect_to_servers`**
- you connect to one server at a time using **`connect_to_server`**
- you shut everything down safely using **`cleanup`**

---

## One-Line Memory Hook

> **Many servers = many sessions, one tool menu, one routing map, and one cleanup manager.**

---

## Another Simple Way to Say It

When the chatbot works with multiple servers, it needs:

- a separate connection to each server
- one combined list of all tools
- a lookup to know which tool belongs to which server
- a safe way to close everything when done

That is the purpose of these new structures and helper methods.

# MCP Chatbot with Line-by-Line Comments

```python
%%writefile mcp_project/mcp_chatbot.py
# Jupyter magic command:
# Writes everything below into the file mcp_project/mcp_chatbot.py

from dotenv import load_dotenv
# Loads environment variables from a .env file

from anthropic import Anthropic
# Imports the Anthropic client used to call the LLM

from mcp import ClientSession, StdioServerParameters, types
# ClientSession -> manages a connection/session to an MCP server
# StdioServerParameters -> holds command/args used to launch an MCP server
# types -> MCP type definitions (not directly used here, but often useful)

from mcp.client.stdio import stdio_client
# Starts communication with an MCP server over standard input/output

from typing import List, Dict, TypedDict
# Type hint helpers:
# List -> list type
# Dict -> dictionary type
# TypedDict -> dictionary with a defined structure

from contextlib import AsyncExitStack
# Helps manage multiple async context managers/resources cleanly

import json
# Used to read the server_config.json file

import asyncio
# Used to run async Python code

load_dotenv()
# Loads values from the .env file into environment variables
# Example: API keys like ANTHROPIC_API_KEY


class ToolDefinition(TypedDict):
    # Defines the shape/structure of a tool description dictionary

    name: str
    # The name of the tool

    description: str
    # A human-readable description of what the tool does

    input_schema: dict
    # The JSON schema describing what input the tool expects


class MCP_ChatBot:
    # Main chatbot class that manages:
    # - MCP server connections
    # - tool discovery
    # - query processing
    # - cleanup

    def __init__(self):
        # Constructor method: runs when a new chatbot object is created

        self.sessions: List[ClientSession] = []
        # Stores all active MCP client sessions
        # One session per server

        self.exit_stack = AsyncExitStack()
        # Tracks async resources (clients/sessions/transports)
        # so they can all be cleaned up safely later

        self.anthropic = Anthropic()
        # Creates the Anthropic client for calling the LLM

        self.available_tools: List[ToolDefinition] = []
        # Master list of all tools exposed by all connected MCP servers

        self.tool_to_session: Dict[str, ClientSession] = {}
        # Maps each tool name to the session/server that owns it
        # Example:
        # "read_file" -> filesystem session
        # "fetch_url" -> fetch session

    async def connect_to_server(self, server_name: str, server_config: dict) -> None:
        # Connects to one MCP server using its configuration

        """Connect to a single MCP server."""

        try:
            server_params = StdioServerParameters(**server_config)
            # Converts the server config dictionary into MCP server parameters
            # Example config:
            # {
            #   "command": "uvx",
            #   "args": ["mcp-server-fetch"]
            # }

            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            # Launches the MCP server as a subprocess and opens stdio transport
            # Using exit_stack ensures the transport is tracked for cleanup later

            read, write = stdio_transport
            # stdio_client returns a pair of streams:
            # read -> receive messages from server
            # write -> send messages to server

            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            # Creates an MCP client session over the read/write streams
            # Also tracked by exit_stack for cleanup

            await session.initialize()
            # Performs MCP session initialization / handshake

            self.sessions.append(session)
            # Stores this session in the list of active sessions

            response = await session.list_tools()
            # Asks the connected server for the list of tools it provides

            tools = response.tools
            # Extracts the tool list from the response

            print(f"\nConnected to {server_name} with tools:", [t.name for t in tools])
            # Prints the connected server name and the names of its tools

            for tool in tools:
                # Loops through every tool provided by this server

                self.tool_to_session[tool.name] = session
                # Records which session/server owns this tool

                self.available_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                })
                # Adds this tool to the master tool list
                # This list is later passed to the LLM so it knows what tools exist

        except Exception as e:
            print(f"Failed to connect to {server_name}: {e}")
            # If this server connection fails, print the error

    async def connect_to_servers(self):
        # Connects to all MCP servers defined in server_config.json

        """Connect to all configured MCP servers."""

        try:
            with open("server_config.json", "r") as file:
                data = json.load(file)
            # Opens and reads the server configuration JSON file

            servers = data.get("mcpServers", {})
            # Gets the "mcpServers" section from the JSON
            # If not found, use an empty dictionary

            for server_name, server_config in servers.items():
                await self.connect_to_server(server_name, server_config)
            # Loops through all configured servers
            # and connects to them one by one

        except Exception as e:
            print(f"Error loading server configuration: {e}")
            # Prints an error if the config file cannot be loaded/read

            raise
            # Re-raises the exception so the caller knows startup failed

    async def process_query(self, query):
        # Handles one user query:
        # - sends it to the LLM
        # - lets the LLM choose tools
        # - routes tool calls to the correct MCP server
        # - returns the final answer

        messages = [{'role': 'user', 'content': query}]
        # Starts the conversation with the user's query

        response = self.anthropic.messages.create(
            max_tokens=2024,
            # Maximum number of tokens allowed in the model response

            # model='claude-3-7-sonnet-20250219', # deprecated model
            model='claude-sonnet-4-6',
            # The Anthropic model being used

            tools=self.available_tools,
            # Passes the full list of discovered tools to the model

            messages=messages
            # Passes the conversation history
        )

        process_query = True
        # Flag used to keep looping until the model gives a final answer

        while process_query:
            # Continue processing until no more tool usage is needed

            assistant_content = []
            # Stores content returned by the assistant in the current response cycle

            for content in response.content:
                # Anthropic may return multiple content blocks
                # Example:
                # - text
                # - tool_use

                if content.type == 'text':
                    # If the model returned plain text

                    print(content.text)
                    # Print the assistant's text response

                    assistant_content.append(content)
                    # Save the text block in assistant content

                    if len(response.content) == 1:
                        process_query = False
                        # If the response only contains text,
                        # then the query is complete

                elif content.type == 'tool_use':
                    # If the model wants to use a tool

                    assistant_content.append(content)
                    # Save the tool request in assistant content

                    messages.append({'role': 'assistant', 'content': assistant_content})
                    # Add the assistant's tool request to conversation history

                    tool_id = content.id
                    # Unique ID of this tool use request

                    tool_args = content.input
                    # Input arguments the model wants to send to the tool

                    tool_name = content.name
                    # Name of the requested tool

                    print(f"Calling tool {tool_name} with args {tool_args}")
                    # Print which tool is being called and with what arguments

                    session = self.tool_to_session[tool_name]
                    # Look up which session/server owns this tool
                    # This is the key routing step

                    result = await session.call_tool(tool_name, arguments=tool_args)
                    # Calls the tool on the correct MCP server

                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": result.content
                            }
                        ]
                    })
                    # Sends the tool result back into the conversation
                    # so the model can continue reasoning

                    response = self.anthropic.messages.create(
                        max_tokens=2024,
                        # Limit output size again

                        # model='claude-3-7-sonnet-20250219', # deprecated model
                        model='claude-sonnet-4-6',
                        # Same model as before

                        tools=self.available_tools,
                        # Same full tool list

                        messages=messages
                        # Updated conversation history including tool results
                    )

                    if len(response.content) == 1 and response.content[0].type == "text":
                        print(response.content[0].text)
                        # If the model now gives only text,
                        # print the final answer

                        process_query = False
                        # Stop the loop because the response is complete

    async def chat_loop(self):
        # Runs an interactive terminal-based chatbot loop

        """Run an interactive chat loop"""

        print("\nMCP Chatbot Started!")
        # Startup message

        print("Type your queries or 'quit' to exit.")
        # Explains how to stop the chatbot

        while True:
            # Infinite loop until user quits

            try:
                query = input("\nQuery: ").strip()
                # Reads user input and removes leading/trailing spaces

                if query.lower() == 'quit':
                    break
                # Exit loop if user types quit

                await self.process_query(query)
                # Process the user's query

                print("\n")
                # Print a blank line after each response

            except Exception as e:
                print(f"\nError: {str(e)}")
                # If anything goes wrong during the query,
                # show the error and continue the loop

    async def cleanup(self):
        # Cleans up all tracked async resources

        """Cleanly close all resources using AsyncExitStack."""

        await self.exit_stack.aclose()
        # Closes all resources stored in exit_stack
        # Example:
        # - client sessions
        # - transports
        # - subprocesses


async def main():
    # Main entry point for the program

    chatbot = MCP_ChatBot()
    # Create the chatbot object

    try:
        # the mcp clients and sessions are not initialized using "with"
        # like in the previous lesson
        # so the cleanup should be manually handled

        await chatbot.connect_to_servers()
        # Reads server_config.json
        # Connects to all MCP servers
        # Discovers all available tools

        await chatbot.chat_loop()
        # Starts the interactive chatbot loop

    finally:
        await chatbot.cleanup()
        # Ensures all sessions/resources are closed
        # even if an error happens


if __name__ == "__main__":
    asyncio.run(main())
    # Runs the async main() function when this file is executed directly

```

