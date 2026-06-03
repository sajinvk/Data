# **MCP Client**
MCP is a protocol where an MCP client connects to an MCP server. The server exposes capabilities such as tools, and the client can discover and call them. 
In your code, Claude is not the MCP client. Your Python program (MCP_ChatBot) is the MCP client. Claude is the LLM that decides which tool to use, while your Python code actually connects to the MCP server and performs the tool call through the MCP session.

## Architecture
* The user typing a question in the console. [modelconte...tocol.info]
* Claude, which reads the question and decides whether a tool is needed via the Messages API. Anthropic describes the Messages API as the direct model-access interface where you manage the conversation and tool loop yourself. [platform.claude.com], [platform.claude.com]
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

