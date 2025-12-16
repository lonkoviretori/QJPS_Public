import os
import shutil
import re
import subprocess
import time

# ==================== 核心配置 ====================
SOURCE_VAULT = r"C:\All\Document\Obsidian\清济平生卷"  # 你的路径
QUARTZ_ROOT = os.getcwd() 
QUARTZ_CONTENT = os.path.join(QUARTZ_ROOT, "content")
COMMIT_MESSAGE = f"Auto deploy: {time.strftime('%Y-%m-%d %H:%M:%S')}"
# ================================================

def run_git_cmd(command, cwd):
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            command, cwd=cwd, shell=True, check=True, 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding='utf-8', errors='replace', env=env
        )
        if result.stdout.strip(): print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {command}\n错误信息: {e.stderr}")
        raise

def step_1_push_to_gitee():
    print("\n📦 [1/3] Gitee 备份...")
    try:
        status = subprocess.run("git status --porcelain", cwd=SOURCE_VAULT, shell=True, stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
        if not status.stdout.strip():
            print("   Gitee 无变动，跳过提交...")
        else:
            run_git_cmd("git add .", SOURCE_VAULT)
            run_git_cmd(f'git commit -m "{COMMIT_MESSAGE}"', SOURCE_VAULT)
    except: pass
    run_git_cmd("git push origin main", SOURCE_VAULT)
    print("✅ Gitee 备份完成")

def step_2_filter_and_copy():
    print("\n🔍 [2/3] 正在扫描并同步公开内容...")
    
    if os.path.exists(QUARTZ_CONTENT):
        shutil.rmtree(QUARTZ_CONTENT)
    os.makedirs(QUARTZ_CONTENT)
    
    copied_count = 0
    scanned_count = 0
    
    for root, dirs, files in os.walk(SOURCE_VAULT):
        if '.git' in root or 'Quartz' in root: continue
        
        for file in files:
            if file.endswith('.md'):
                scanned_count += 1
                src_path = os.path.join(root, file)
                
                # --- 增强的判断逻辑 ---
                is_pub = False
                try:
                    with open(src_path, 'r', encoding='utf-8') as f:
                        content = f.read() # 读取全文（如果是特别大的文件，read()可能耗内存，但笔记一般没事）
                        
                        # 正则解释：
                        # ^\s* -> 行首允许有空格
                        # publish: -> 匹配 publish:
                        # \s* -> 允许冒号后有任意个空格
                        # true -> 匹配 true (忽略大小写)
                        if re.search(r'^\s*publish:\s*true', content, re.MULTILINE | re.IGNORECASE):
                            is_pub = True
                except Exception as e:
                    print(f"⚠️ 读取失败: {file} - {e}")
                
                if is_pub:
                    rel_path = os.path.relpath(src_path, SOURCE_VAULT)
                    dest_path = os.path.join(QUARTZ_CONTENT, rel_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    print(f"  [+] 发现并同步: {file}")
                    copied_count += 1
    
    # 图片同步
    src_assets = os.path.join(SOURCE_VAULT, "assets") 
    dest_assets = os.path.join(QUARTZ_CONTENT, "assets")
    if os.path.exists(src_assets):
        shutil.copytree(src_assets, dest_assets)
        print("  [+] 同步图片附件目录")

    print(f"✅ 扫描了 {scanned_count} 个文件，同步了 {copied_count} 篇文章。")

def step_3_push_to_github():
    print("\n🚀 [3/3] GitHub 发布...")
    run_git_cmd("git add .", QUARTZ_ROOT)
    try:
        status = subprocess.run("git status --porcelain", cwd=QUARTZ_ROOT, shell=True, stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
        if status.stdout.strip():
            run_git_cmd(f'git commit -m "{COMMIT_MESSAGE}"', QUARTZ_ROOT)
        else:
            print("   GitHub 内容无变动...")
    except: pass
    run_git_cmd("git push origin main", QUARTZ_ROOT)
    print("✅ GitHub 推送完成")

if __name__ == "__main__":
    try:
        step_1_push_to_gitee()
        step_2_filter_and_copy()
        step_3_push_to_github()
        print("\n🎉 全流程成功！")
    except Exception as e:
        print(f"\n❌ 中断: {e}")
        input("按回车键退出...")