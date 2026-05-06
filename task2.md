agentob第二次迭代的任务书
第一次迭代的任务书在 task.md中，实际的开发情况，请见agent-observer\DELIVERY.md和
agent-observer\README.md。请你再次的基础上开发剩余的两个功能

## 基于大模型的 agent 调用分析

### 输入输出
输入是mitm解析生成的.agentob\[session_id]\decoded_flows\analyzed文件夹
输出是一个analyze.json，包含对analyzed中各个部分的解读，输出的详细细节见下面的说明
- 分析结果语言为中文，只有引用或者特定术语使用英文
- 1. 分析系统提示词，总结出当前agent的工作模式
- 2. 分析可用工具列表，简要记录当前可用的系统工具
- 3. 针对call_trace.json中的每次调用进行独立分析，具体来说：
    - 使用LLM api进行分析，你需要设计合适的提示词模版，以及一个env文件记录api的url和key（采用anthropic兼容的api格式）
    - 考虑到上下文限制，每次分析一个调用他的输入是已经生成的部分analyze.json，以及对
      应要分析的调用json的那一项和他的前五项。注意这里的每一项不是index，而是所
      有information_list列表的每一项。每一项的形式是{"type":...,"...":...,...},
      输出是两个字符串，一是本项的大意信息（写入analyze.json供后续分析参考，工具调用
      需要保留原始的调用参数），二是分析本项的意图以及评分
    - 整理完所有的调用项之后，根据analyze.json,生成整体的分析报告，也是一个字符串
    - 如果遇到什么错误，也要生成analyze.json，格式一致，字符串留空即可
    - 你可以使用已经生成的.agentob\b844fa93分析输入的结构，以及测试（只需要测试失败场景即可，成功的场景需要我手动配置api）

## 结果可视化

当所有分析都结束后，将analyzed文件夹以及agent 调用分析结果，绘制到一个可交互的动态网页上，供开发人员查看这次调用的具体情况，具体的样式可以参考claude-devtools这个开发工具，他的路径为claude-devtools
