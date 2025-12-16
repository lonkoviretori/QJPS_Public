import os
import shutil
import re
import subprocess
import time

# ==================== 核心配置 (请修改这里) ====================
# 1. 你的 Obsidian 笔记库路径 (对应 Gitee 私有库)
SOURCE_VAULT = r"C:\All\Document\Obsidian\清济平生卷"

# 2. Quartz 项目路径 (对应 GitHub 公开库)
QUARTZ_ROOT = os.getcwd() 
QUARTZ_CONTENT = os.path.join(QUARTZ_ROOT, "content")

# 3. 提交信息
COMMIT_MESSAGE = f"Auto deploy: {time.strftime('%Y-%m-%d %H:%M:%S')}"
# ============================================================

def run_git_cmd(command, cwd):
    """专门用来运行 Git 命令，强制使用 UTF-8 编码，防止中文报错"""
    try:
        # 强制设置环境变量，让 Git 输出 UTF-8
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(
            command, 
            cwd=cwd, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',     # 关键修复：强制用 UTF-8 读取
            errors='replace',     # 关键修复：遇到读不懂的字符用 ? 代替，别报错
            env=env
        )
        # 只有当有输出内容时才打印，保持界面清爽
        if result.stdout.strip():
            print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {command}")
        print(f"错误信息: {e.stderr}")
        raise # 抛出异常，停止后续步骤

def step_1_push_to_gitee():
    """步骤一：将所有文件备份到 Gitee (私有库)"""
    print("\n========================================")
    print("📦 步骤 1/3: 正在全量备份到 Gitee...")
    print("========================================")
    
    # 检查是否有变更
    try:
        # 这里也要加 encoding='utf-8'
        status = subprocess.run(
            "git status --porcelain", 
            cwd=SOURCE_VAULT, 
            shell=True, 
            stdout=subprocess.PIPE, 
            text=True, 
            encoding='utf-8', 
            errors='replace'
        )
        
        if not status.stdout.strip():
            print("Gitee 仓库无变动，跳过提交，尝试直接推送...")
        else:
            run_git_cmd("git add .", SOURCE_VAULT)
            run_git_cmd(f'git commit -m "{COMMIT_MESSAGE}"', SOURCE_VAULT)
    except Exception as e:
        print(f"⚠️ 检测状态时出现小问题 (可忽略): {e}")

    # 推送到 Gitee
    run_git_cmd("git push origin main", SOURCE_VAULT)
    print("✅ Gitee 备份完成！")

def step_2_filter_and_copy():
    """步骤二：筛选公开文件搬运到 Quartz"""
    print("\n========================================")
    print("🔍 步骤 2/3: 正在筛选并同步公开内容...")
    print("========================================")
    
    # 1. 清理旧内容
    if os.path.exists(QUARTZ_CONTENT):
        shutil.rmtree(QUARTZ_CONTENT)
    os.makedirs(QUARTZ_CONTENT)
    
    copied_count = 0
    
    # 2. 遍历并筛选
    for root, dirs, files in os.walk(SOURCE_VAULT):
        if '.git' in root or 'Quartz' in root: continue
        
        for file in files:
            if file.endswith('.md'):
                src_path = os.path.join(root, file)
                
                # 判断 publish: true
                is_pub = False
                try:
                    with open(src_path, 'r', encoding='utf-8') as f:
                        head = [next(f) for _ in range(50)]
                        if re.search(r'^publish:\s*true', ''.join(head), re.MULTILINE):
                            is_pub = True
                except: pass
                
                if is_pub:
                    rel_path = os.path.relpath(src_path, SOURCE_VAULT)
                    dest_path = os.path.join(QUARTZ_CONTENT, rel_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    print(f"  [+] 同步文章: {rel_path}")
                    copied_count += 1
    
    # 3. 处理图片
    src_assets = os.path.join(SOURCE_VAULT, "assets") 
    dest_assets = os.path.join(QUARTZ_CONTENT, "assets")
    if os.path.exists(src_assets):
        shutil.copytree(src_assets, dest_assets)
        print("  [+] 同步图片附件")

    print(f"✅ 内容处理完成，共同步 {copied_count} 篇文章。")

def step_3_push_to_github():
    """步骤三：将公开内容推送到 GitHub"""
    print("\n========================================")
    print("🚀 步骤 3/3: 正在发布到 GitHub...")
    print("========================================")
    
    run_git_cmd("git add .", QUARTZ_ROOT)
    
    try:
        # 检查是否有变动再提交
        status = subprocess.run(
            "git status --porcelain", 
            cwd=QUARTZ_ROOT, 
            shell=True, 
            stdout=subprocess.PIPE, 
            text=True, 
            encoding='utf-8', 
            errors='replace'
        )
        if status.stdout.strip():
            run_git_cmd(f'git commit -m "{COMMIT_MESSAGE}"', QUARTZ_ROOT)
        else:
            print("⚠️ GitHub 内容无变动，继续推送...")
    except:
        pass
        
    run_git_cmd("git push origin main", QUARTZ_ROOT)
    print("✅ GitHub 推送完成！网站将由 Vercel 自动更新。")

if __name__ == "__main__":
    try:
        step_1_push_to_gitee()
        step_2_filter_and_copy()
        step_3_push_to_github()
        print("\n🎉🎉🎉 全流程执行成功！")
    except Exception as e:
        print(f"\n❌ 流程中断: {e}")
        input("按回车键退出...")