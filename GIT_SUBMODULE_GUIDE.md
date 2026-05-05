# Git 子模块提交和推送指南

## 当前情况

- `agent-observer` 是父仓库 `agob_workspace` 的一个子模块
- 子模块当前处于 detached HEAD 状态
- 需要先提交子模块，再更新父仓库

## 完整操作步骤

### 步骤 1: 提交子模块 (agent-observer)

```bash
# 进入子模块目录
cd agent-observer

# 检查当前状态
git status

# 切换到主分支（如果处于 detached HEAD 状态）
git checkout main
# 或者创建新分支
# git checkout -b feature/initial-implementation

# 添加所有新文件
git add .

# 查看将要提交的内容
git status

# 提交更改
git commit -m "feat: initial implementation of agentob tool

- Add CLI interface with argument parsing
- Implement wrapper for mitmproxy management
- Add decoder for mitm file parsing with SSE support
- Add analyzer for request simplification and extraction
- Add comprehensive documentation (README, QUICKSTART, etc.)
- Add installation scripts for Windows and Linux
- Add usage examples"

# 推送到远程仓库
git push origin main
# 如果是新分支
# git push -u origin feature/initial-implementation
```

### 步骤 2: 更新父仓库 (agob_workspace)

```bash
# 返回父仓库目录
cd ..

# 查看状态（会看到 agent-observer 子模块有更新）
git status

# 添加子模块的更新
git add agent-observer

# 如果有其他更改也一起添加
git add task.md  # 如果修改了

# 提交父仓库的更改
git commit -m "chore: update agent-observer submodule

- Complete initial implementation of agentob tool
- Add all core modules and documentation"

# 推送父仓库
git push origin main
```

## 常用命令速查

### 子模块操作

```bash
# 查看子模块状态
git submodule status

# 更新子模块到最新提交
git submodule update --remote agent-observer

# 初始化和更新所有子模块
git submodule update --init --recursive
```

### 处理 detached HEAD

```bash
# 方法 1: 切换到已有分支
cd agent-observer
git checkout main

# 方法 2: 基于当前提交创建新分支
cd agent-observer
git checkout -b feature/my-feature

# 方法 3: 查看所有分支
git branch -a
```

### 一键提交脚本（推荐）

创建一个脚本 `commit_all.sh`:

```bash
#!/bin/bash
set -e

echo "=========================================="
echo "提交 agent-observer 子模块"
echo "=========================================="

cd agent-observer

# 确保在正确的分支上
if git symbolic-ref -q HEAD > /dev/null; then
    echo "当前分支: $(git branch --show-current)"
else
    echo "警告: 处于 detached HEAD 状态，切换到 main 分支"
    git checkout main
fi

# 添加所有更改
git add .

# 提交
echo "请输入子模块提交信息:"
read -r commit_msg
git commit -m "$commit_msg"

# 推送
git push origin $(git branch --show-current)

echo ""
echo "=========================================="
echo "更新父仓库"
echo "=========================================="

cd ..

# 添加子模块更新
git add agent-observer

# 提交父仓库
git commit -m "chore: update agent-observer submodule"

# 推送父仓库
git push origin main

echo ""
echo "=========================================="
echo "完成！"
echo "=========================================="
```

使用方法:
```bash
chmod +x commit_all.sh
./commit_all.sh
```

## Windows 版本 (commit_all.bat)

```batch
@echo off
echo ==========================================
echo 提交 agent-observer 子模块
echo ==========================================

cd agent-observer

REM 检查是否在分支上
git symbolic-ref -q HEAD >nul 2>&1
if errorlevel 1 (
    echo 警告: 处于 detached HEAD 状态，切换到 main 分支
    git checkout main
)

REM 添加所有更改
git add .

REM 提交
set /p commit_msg="请输入子模块提交信息: "
git commit -m "%commit_msg%"

REM 推送
for /f "tokens=*" %%i in ('git branch --show-current') do set current_branch=%%i
git push origin %current_branch%

echo.
echo ==========================================
echo 更新父仓库
echo ==========================================

cd ..

REM 添加子模块更新
git add agent-observer

REM 提交父仓库
git commit -m "chore: update agent-observer submodule"

REM 推送父仓库
git push origin main

echo.
echo ==========================================
echo 完成！
echo ==========================================
pause
```

## 注意事项

1. **先提交子模块，再提交父仓库**
   - 父仓库只记录子模块的 commit hash
   - 必须先推送子模块，父仓库才能正确引用

2. **避免 detached HEAD**
   - 在子模块中工作前，确保切换到某个分支
   - 使用 `git checkout main` 或创建新分支

3. **查看子模块状态**
   ```bash
   # 在父仓库中
   git submodule status
   # 输出示例:
   # +e57c16a agent-observer (heads/main)
   # 前面的 + 表示子模块有未提交的更改
   ```

4. **克隆包含子模块的仓库**
   ```bash
   git clone --recursive <repository-url>
   # 或者
   git clone <repository-url>
   cd <repository>
   git submodule update --init --recursive
   ```

5. **子模块更新后同步**
   - 其他人拉取父仓库后，需要运行:
   ```bash
   git pull
   git submodule update --init --recursive
   ```

## 快速操作（当前情况）

```bash
# 1. 进入子模块并切换到 main 分支
cd agent-observer
git checkout main

# 2. 添加并提交所有文件
git add .
git commit -m "feat: initial implementation of agentob tool"
git push origin main

# 3. 返回父仓库并更新子模块引用
cd ..
git add agent-observer
git commit -m "chore: update agent-observer submodule"
git push origin main
```

## 故障排查

### 问题 1: 推送被拒绝

```bash
# 先拉取最新代码
git pull --rebase origin main
# 然后再推送
git push origin main
```

### 问题 2: 子模块冲突

```bash
# 在父仓库中
git submodule update --remote --merge agent-observer
```

### 问题 3: 忘记推送子模块

如果父仓库已经推送，但子模块忘记推送：
```bash
cd agent-observer
git push origin main
```

其他人拉取时会看到子模块引用的 commit 不存在，需要你补推。
