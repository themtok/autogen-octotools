# Autogen-Octotools：Agentic框架实现

本项目是下述论文中描述的Agentic框架的一种实现：

**[OctoTools: An Agentic Framework with Extensible Tools for Complex Reasoning](https://arxiv.org/abs/2502.11271)**

> *Pan Lu, Bowen Chen, Sheng Liu, Rahul Thapa, Joseph Boen, James Zou (2025)*

## 概述

本代码库提供了一个模块化、可扩展的Agentic框架，用于复杂推理，其灵感来源于OctoTools论文。该实现构建于[Microsoft AutoGen 框架](https://microsoft.github.io/autogen/stable/)之上，利用了其强大的代理编排和工具集成能力。

OctoTools引入了标准化的工具卡、用于高层和低层规划的规划器以及用于工具使用的执行器。该框架设计为无需训练、用户友好且易于扩展，支持跨领域的广泛推理任务。

## 特性

- 基于 [Microsoft AutoGen](https://microsoft.github.io/autogen/stable/) 构建
- 用于代理编排的模块化运行时
- 标准化工具接口，易于扩展
- 内置工具：Wikipedia搜索、网络搜索、新闻API、内容提取、通用工具、API调用器、评论器
- 高层和低层规划
- 多步推理和工具链
- 异步支持可扩展工作流

## 要求

- Python 3.8+
- 依赖项请参见 `reuirements.txt`

## 安装

1.  克隆代码库：

    ```powershell
    git clone <repo-url>
    cd otools-autogen
    ```
2.  安装依赖项：

    ```powershell
    pip install -r reuirements.txt
    ```
3.  （可选）在 `.env` 文件中设置环境变量，用于API密钥和配置。
    需要的值：OPENROUTER_API_KEY, OPENROUTER_BASE_PATH

## 使用方法

运行示例用法脚本：

```powershell
python example_usage.py
```

这将启动运行时，注册所有工具，并演示一个示例代理工作流。

## 项目结构

-   `otools_autogen/` - 核心框架和运行时
-   `tools/` - 内置和自定义工具
-   `example_usage.py` - 演示用法的示例脚本
-   `reuirements.txt` - Python 依赖项

## 添加新工具

1.  在 `tools/` 目录中创建一个新工具。
2.  在您的脚本中使用 `runtime.register_tool()` 注册该工具。

## 免责声明

实现的许多部分（如提示）的灵感来自于Octotools的原始实现 - [octotools](https://github.com/octotools/octotools)

本项目未实现原始论文中描述的特定任务工具集优化 - 工具由规划器代理从完整的工具集中自主选择。

## 参考资料

-   论文：[OctoTools: An Agentic Framework with Extensible Tools for Complex Reasoning](https://arxiv.org/abs/2502.11271)
-   Microsoft AutoGen：[https://microsoft.github.io/autogen/stable/](https://microsoft.github.io/autogen/stable/)
-   许可证：MIT
