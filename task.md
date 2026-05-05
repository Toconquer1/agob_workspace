当前的任务是构建一个 python package 形式的 agent 执行过程观测工具 agentob。
他的核心过程为通过一个 Python wrapper 管理整个观测周期，例如执行 agentob -- claude 命令后：

# 总体过程

1. 检查当前是否在指定路径安装了 mitmproxy，否则安装。然后启动代理服务，并监听 8080 端口。
2. 设置环境变量，包含系统代理，证书配置等，如下 bash 代码所示。

```bash
set HTTP_PROXY=http://127.0.0.1:8080
set HTTPS_PROXY=http://127.0.0.1:8080
# 如果为node.js应用，如claude code，那么要执行
set NODE_TLS_REJECT_UNAUTHORIZED=0
# 如果为python应用，如langchain，那么要执行
set REQUESTS_CA_BUNDLE=~/.mitmproxy/mitmproxy-ca-cert.pem
set SSL_CERT_FILE=~/.mitmproxy/mitmproxy-ca-cert.pem
```

3. 根据用户传入的命令，创建子进程执行对应的 agent 应用，使用户和 agent 进行交互，同时代理抓取所有的 LLM 请求
4. 用户关闭 agent 退出子进程，Python wrapper 获取 mitm 文件
5. 通过脚本将 mitm 解析成系统提示词，工具列表，以及每一轮的调用过程等信息
6. 根据分析结果利用 llm 总结每一次调用的过程，并汇总整个调用过程的情况（）
7. 将 5 和 6 的结果通过网页形式做一个可视化页面

# 工具产物要求

- 这个工具需要适配 windows/linux 系统，并且支持 openai/anthropic 兼容的接口
- 这个工具本身的相关代码必须存放在 agent-observer 这个仓库当中，他最后的形式是一个 python package，打包好之后可以在任意的目录调用这个工具，将解析结果存放在当前文件夹
- 外层目录 agob_workspace 是辅助开发 agent-observer 的目录，他只存放参考资料，或者一些测试文件夹
- 总体过程所说的就是这个工具的全部功能，不要加上其他的实现方法

# 开发方法

一定要逐步实现这个工具，不要一口气全部做好，并且 agent-observer 这个项目中需要一个 md 详细说明如何使用

# 具体内容

## Python wrapper 的框架设计

通用 Python wrapper（参考 wrap_agent.py），用户通过 python wrap_agent.py -- <目标命令> 启动 agent 应用；wrapper 解析 -- 后面的命令，将第一个参数用 shutil.which() 替换成真实可执行路径，后续参数原样保留，；wrapper 在启动前构造一份继承当前系统环境的 env，向其中注入 HTTP_PROXY、HTTPS_PROXY 以及自定义变量，然后用 subprocess.Popen 启动真实的目标命令，并让子进程继承当前终端的 stdin/stdout/stderr，从而保留目标应用的原生命令行交互体验；当目标应用退出后，wrapper 主进程继续执行后处理逻辑。

## 安装 mitmproxy 并启动代理工具

只使用 python pip 安装这个代理工具，然后这个代理可以将流文件 mitm 存放在当前目录的指定输出文件夹中。注意证书和可执行文件路径的处理

## 解析 mitm 文件

### 功能需求

总体需求：用户通过 Python wrapper 打开一个 agent 并执行一些任务，收集 agent 运行过程的网络流量，得到整个 agent 的调用轨迹结果（具体形式可以为多个 json，如果你有更好的想法也可以自己定义）

具体细节（非常重要）：

1. 我们是针对 agent 系统的网络请求进行抓包分析，关注的流量目前有两类，一个是 LLM 的请求流量，另外一个是 mcp 的调用请求，请你在收集的时候根据 url 区分处理不同的请求
2. 输出内容：

- 系统提示词/工具列表/skill 列表/mcp 的信息可以单独提取出来，成为单独的 json，主调用 json 里引用即可
- 主调用 json 包含模型的思考，mcp/工具调用的参数和返回结果，以及子 agent 的调用过程，就安装一个信息列表的方式来组织，包括用户信息，工具调用信息，模型思考信息，子 agnet 信息四种（如果不够，你可以自行定义）

3. 整个 agent 运行的流程中，请求包含多个 LLM 请求响应对以及 mcp，除了最后一次响应以外，其他的响应内容理论上会包括在下一次的请求中，所以对于这种重复出现的内容你只需要校验 mcp/llm 响应的内容，和下一次 llm 请求中是否一样即可，一样则在对应的内容上加上标志属性，如果出现不一致的情况，则将不一样的内容追加到这一项的 json 属性中

4. 对于内部工具调用，llm 会将工具的返回结果以用户角色的形式拼在上下文里，请你区别这种内容，将这种内容视为工具调用信息，而不是用户给出的信息
5. 对于这个部分你可以写一个测试类，输入文件为 analyze-claude-flows-example\flows_no_skill_prompts.mitm

### analyze-claude-flows 介绍

这个部分我之前写了一个 skill 结合两个 python 脚本，解析 llm 请求相应，并提取所需信息，在做这个步骤的时候，请你参考这个 skill 中的 skills\analyze-claude-flows\scripts 中的两个脚本文件，以及这个 skill 的示例输入输出 analyze-claude-flows-example，开发这个功能。

decode_mitmproxy_flow.py 是 mitm 解码脚本。输入是 mitm 文件，输出是一个文件夹，将每一个请求相应对的 json 解码出来，他能够处理 sse 格式数据
simplify_prompts.py 是简化请求 json 脚本，他能够实现两个功能，1.提取多次请求中相同的系统提示词以及工具列表等信息 2. 解析相邻 json 请求中增量的内容，标记相同的已经出现过的内容
agob_workspace\analyze-claude-flows-example\flows_no_skill_prompts.txt_analysis_result\parsed_jsons 中的结果即为这两个脚本解析后的结果文件

## ！！！请你先实现到此之前的功能，接下来的两个功能，下一次迭代生成

## 基于大模型的 agent 调用分析

## 结果可视化
