# Autogen-Octotools: Agentic Framework Implementation

This project is an implementation of the agentic framework described in the paper:

**[OctoTools: An Agentic Framework with Extensible Tools for Complex Reasoning](https://arxiv.org/abs/2502.11271)**

> *Pan Lu, Bowen Chen, Sheng Liu, Rahul Thapa, Joseph Boen, James Zou (2025)*

## Overview

This repository provides a modular, extensible agentic framework for complex reasoning, inspired by the OctoTools paper. The implementation is built on top of the [Microsoft AutoGen framework](https://microsoft.github.io/autogen/stable/), leveraging its robust agent orchestration and tool integration capabilities.

OctoTools introduces standardized tool cards, a planner for high- and low-level planning, and an executor for tool usage. The framework is designed to be training-free, user-friendly, and easily extensible, supporting a wide range of reasoning tasks across domains.

## Features

- Built on [Microsoft AutoGen](https://microsoft.github.io/autogen/stable/)
- Modular runtime for agent orchestration
- Standardized tool interface for easy extension
- Built-in tools: Wikipedia search, web search, news API, content extraction, generalist, API caller, critic
- High-level and low-level planning
- Multi-step reasoning and tool chaining
- Async support for scalable workflows

## Requirements

- Python 3.8+
- See `reuirements.txt` for dependencies

## Installation

1. Clone the repository:

   ```powershell
   git clone <repo-url>
   cd otools-autogen
   ```

2. Install dependencies:

   ```powershell
   pip install -r reuirements.txt
   ```

3. (Optional) Set up environment variables in a `.env` file for API keys and configuration.
    Values needed: OPENROUTER_API_KEY,OPENROUTER_BASE_PATH

## Usage

Run the example usage script:

```powershell
python example_usage.py
```

This will start the runtime, register all tools, and demonstrate a sample agent workflow.

## Project Structure

- `otools_autogen/` - Core framework and runtime
- `tools/` - Built-in and custom tools
- `example_usage.py` - Example script demonstrating usage
- `reuirements.txt` - Python dependencies

## Adding New Tools

1. Create a new tool in the `tools/` directory.
2. Register the tool in your script using `runtime.register_tool()`.

## Disclaimer

Many parts of implementations (like prompts) were inspired by original Octotools implemenation - [octotools](https://github.com/octotools/octotools)
Project does not implement Task-specific Toolset Optimization descibed in original paper- tools are selcted autonomously by planner agent from complete polulation of tools.

## References

- Paper: [OctoTools: An Agentic Framework with Extensible Tools for Complex Reasoning](https://arxiv.org/abs/2502.11271)
- Microsoft AutoGen: [https://microsoft.github.io/autogen/stable/](https://microsoft.github.io/autogen/stable/)
- License: MIT
