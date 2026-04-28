





通用 Python wrapper（参考 wrap_agent.py），用户通过 python wrap_agent.py -- <目标命令> 启动 agent 应用；wrapper 解析 -- 后面的命令，将第一个参数用 shutil.which() 替换成真实可执行路径，后续参数原样保留，；wrapper 在启动前构造一份继承当前系统环境的 env，向其中注入 HTTP_PROXY、HTTPS_PROXY以及自定义变量，然后用 subprocess.Popen 启动真实的目标命令，并让子进程继承当前终端的 stdin/stdout/stderr，从而保留目标应用的原生命令行交互体验；当目标应用退出后，wrapper 主进程继续执行后处理逻辑，例如停止 mitmproxy、解析 .mitm 抓包文件并生成可视化报告。

