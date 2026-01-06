---
publish: true
---


### 1.配置环境变量
在系统环境变量中，Path中，新建三个环境变量，分别是：
1. C:\All\Software\Miniforge3
2. C:\All\Software\Miniforge3\Scripts
3. C:\All\Software\Miniforge3\Library\bin
然后都确定并保存。
检验：在命令指示符中输入：
conda --version
如果正常显示版本号就没问题。


### 2.配置清华源
在C:\Users\用户名 下，创建一个.condarc文件，其中内容为：
```
channels:
  - defaults
show_channel_urls: true
default_channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  msys2: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  bioconda: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  menpo: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch-lts: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  simpleitk: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
```
用于配置清华源，然后在命令指示符中：
conda clean -i
conda config --show channels

检验：
conda info
看urls中有没有清华的网址。

### 3.后续使用
简单的回答是：**是的，对于99%的日常操作（装包、创建环境），你只需要把 `conda` 换成 `mamba`，剩下的命令格式完全一样。**

但为了让你用得更明白、更专业，这里有一个精准的**“最佳实践法则”**，帮你区分什么时候用哪个：

#### 1. 什么时候必须/最好用 `mamba`？（为了速度）
凡是涉及到**“计算依赖”、“下载”、“安装”、“卸载”**这种需要花时间的操作，**请务必用 `mamba`**。因为它是用 C++ 写的，解算依赖的速度比 Python 写的 Conda 快几十倍。

*   **创建环境**：
    *   ❌ `conda create -n myenv python=3.10` (慢，可能卡在 Solving environment)
    *   ✅ `mamba create -n myenv python=3.10` (**秒杀**)
*   **安装包**：
    *   ❌ `conda install pandas`
    *   ✅ `mamba install pandas`
*   **搜索包**：
    *   ✅ `mamba search pytorch`

#### 2. 什么时候继续用 `conda`？（为了兼容和习惯）
涉及到**“系统设置”**、**“环境切换”**的操作，建议继续使用 `conda` 命令。虽然 `mamba` 也能做部分此类操作，但 `conda` 是官方标准，兼容性最好。

*   **激活/退出环境**（最常用）：
    *   ✅ `conda activate myenv`
    *   ✅ `conda deactivate`
    *   *(注：虽然 `mamba activate` 也能用，但它本质上还是调用 conda，不如直接用 conda 顺手)*
*   **修改配置**（比如刚才的换源）：
    *   ✅ `conda config ...`
*   **初始化 Shell**：
    *   ✅ `conda init`

#### 3. 一张表总结

| 操作类型 | 推荐命令 | 理由 |
| :--- | :--- | :--- |
| **安装软件** (Install) | `mamba install xxx` | **极速**，不卡顿 |
| **创建环境** (Create) | `mamba create ...` | **极速**，不卡顿 |
| **卸载软件** (Remove) | `mamba remove xxx` | 快速 |
| **激活环境** (Activate) | `conda activate xxx` | 经典，稳定 |
| **查看列表** (List) | `mamba list` / `conda list` | 两者没区别，看心情 |
| **修改配置** (Config) | `conda config ...` | 官方管理工具 |

---

#### 💡 一个小贴士
Miniforge 里是**同时包含** `conda` 和 `mamba` 的。
如果你某天忘记了拼写，随手敲了 `conda install ...`，它也是能运行的，**不会报错**，只是速度会变慢（变回原来的龟速）。

所以，养成肌肉记忆：**装东西就敲 mamba，切环境就敲 conda。**