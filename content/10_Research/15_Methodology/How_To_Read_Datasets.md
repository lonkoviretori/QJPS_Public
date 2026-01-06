---
publish: true
---
# 数据集阅读与组织教程笔记

## 一、 概括：数据管理的底层逻辑
在管理大规模数据集时，混乱的文件名和目录结构是最大的敌人。一个优秀的结构应该让任何人（包括几个月后的你自己）都能一眼看懂数据的**来源**、**类型**和**处理阶段**。
本文主要讲解：
1. 数据集中如何给文件和目录命名。
2. 数据集中文件如何分类，也就是放到哪个目录下。

在接触任何一个新的数据集时，我们首先要理解它的“语言”。一个专业的数据集通常遵循两条核心逻辑：

1.  **命名即索引 (Naming as Indexing)**：
    *   文件名不是随便起的，它是一个**数据库查询语句**。
    *   **公式**：`[前缀/项目名]_[样本ID]_[实验条件/任务]_[具体模态].[格式]`
    *   **原则**：机器可读（无空格、统一连接符）、排序友好（ID置前）、后缀表意（一眼看出是图片还是表格）。

2.  **目录即生命周期 (Directory as Lifecycle)**：
    *   文件放在哪里，取决于它处于数据处理的哪个阶段。
    *   **Raw / Source**：不可触碰的原始数据（只读）。
    *   **Derivatives**：经过软件处理、清洗后的中间产物（主要工作区）。
    *   **Results / Stats**：高度浓缩的统计结果（如特征向量、模型权重）。

---

## 二、 案例分析 I：扁平化功能型结构
**——以 Natural Scenes Dataset (NSD) 为例**

这种结构常见于**超大规模、单一类型**的数据集（如云端存储 S3）。它的特点是**“按数据类型分桶”**，而不是按受试者分桶。

### 1. 顶层结构深度解读
观察 AWS S3 的文件列表，我们看到所有文件夹都平铺在根目录下，这是一种**“横向扩展”**的架构。

*   **`nsddata_rawdata/` (原始数据仓库)**
    *   **定义**：这是从 fMRI 扫描仪直接导出的数据（通常是 DICOM 或未经转换的 NIfTI）。
    *   **特征**：包含完整的噪声、头动伪影。它是整个项目的“备份底片”。
    *   **警告**：除非你是要做去噪算法研究，否则一般**不要**直接使用这里的数据，处理难度极大。

*   **`nsddata/` (核心预处理数据)**
    *   **定义**：这是官方推荐使用的标准版本。
    *   **特征**：通常已经做过切片层时校正 (Slice-timing)、头动校正 (Motion Correction) 和配准 (Registration)。
    *   **使用场景**：绝大多数研究者的起点。

*   **`nsddata_betas/` (高阶分析产物)**
    *   **定义**：**Betas** 在统计学/脑科学中特指 GLM（一般线性模型）的回归系数。
    *   **实质**：这不仅仅是“图像”，而是**“特征”**。它代表了大脑对某张图片的反应强度，剔除了基线漂移等噪音。
    *   **价值**：如果你做机器学习或解码（Decoding）任务，直接拿这个文件夹的数据最省事，因为它已经是提取好的特征了。

*   **`nsddata_stimuli/` (实验素材/自变量)**
    *   **定义**：这里存放的不是脑数据，而是**受试者当时看到的图片**（如 73,000 张 COCO 数据集图片）。
    *   **关系**：这是实验的“输入 (X)”，而上面的 `nsddata` 是实验的“输出 (Y)”。做多模态研究时，需要将这里的图片与脑数据一一对应。

---

## 三、 案例分析 II：层级化个体型结构
**——以 GOD (Generic Object Decoding) 数据集为例**

这种结构遵循 **BIDS (Brain Imaging Data Structure)** 标准，是目前科学界最严谨的管理方式。它的特点是**“以个体为中心，纵向深度极深，文件类型极其丰富”**。

### 1. 顶层三大支柱：数据的三种形态
通过目录树，我们首先看到三个平行的顶级目录，它们代表了数据在不同处理阶段的形态：

*   **`sub-xx/` (原始核心)**：
    *   **内容**：存放经过格式化但未去噪的“半成品”。包含具体的图像 (`.nii`) 和行为时间表 (`.tsv`)。
    *   **用途**：这是数据集的躯干。如果你的研究需要尝试全新的预处理方法，请从这里开始。

*   **`derivatives/` (加工产物)**：
    *   **路径含义**：`derivatives > preproc-spm > output`。
    *   **解读**：这行路径明确记录了处理流水线——使用了 **SPM 软件** 进行了 **预处理 (preproc)**。这体现了科研的可追溯性。如果下次用 FSL 软件处理，就会多出一个 `preproc-fsl` 目录。

*   **`sourcedata/` (定义与元数据)**：
    *   **特殊性**：在这个数据集中，它存放的不是原始扫描图，而是极为珍贵的 **ROI Masks (感兴趣区掩膜)**。
    *   **文件举例**：`sub-01_mask_LH_FFA.nii.gz`。
    *   **解读**：
        *   `LH` = Left Hemisphere (左脑)。
        *   `FFA` = Fusiform Face Area (梭状回面孔区，专门负责看脸的区域)。
    *   **作用**：这些文件就像“地图的图层”，研究者贴心地帮我们把大脑中“专门负责看人脸”、“专门负责看物体”的区域画出来了。我们不需要全脑分析，直接用这些 Mask 提取信号即可。

### 2. 文件格式全解析：后缀名背后的科学含义
在进入具体文件夹前，我们需要读懂几种特定的文件后缀，它们各司其职，缺一不可：

#### A. `*.nii.gz` (神经影像数据 / Neuroimaging)
这是数据集的核心主体，相当于“录像带”或“3D照片”。
*   **含义**：NIfTI 格式的压缩包 (GZip)。
*   **分类解读**：
    *   **`_T1w.nii.gz` (解剖像)**：这是一张**静态的高清3D大脑照片**。分辨率极高（通常 1mm），能看清大脑的沟回结构，但没有时间维度。**用途：** 作为地图底板，用于定位。
    *   **`_bold.nii.gz` (功能像)**：这是一段**低清的4D大脑录像**（3D空间 + 时间）。分辨率较低（颗粒感强），但它记录了大脑每隔几秒钟的血流变化。**用途：** 分析大脑在想什么。
    *   **`_mask.nii.gz` (掩膜)**：这是一个**二进制文件**（只有0和1）。1代表选中的区域（如视觉皮层），0代表背景。**用途：** 像剪纸一样，把感兴趣的脑区“抠”出来。

#### B. `*.tsv` (事件记录表 / Tab-Separated Values)
这是实验的“剧本”，必须与影像配合使用。
*   **含义**：以制表符分隔的表格文件，可用 Excel 打开。
*   **内容结构**：通常包含以下列：
    *   `onset`: 事件发生的具体时间（秒）。
    *   `duration`: 事件持续了多久。
    *   `trial_type` / `stim_file`: 这一刻受试者看的是“苹果”还是“香蕉”。
*   **重要性**：只有 `.nii.gz` 你只能看到脑子在亮，有了 `.tsv` 你才知道**“哦，原来脑子亮是因为看到了苹果”**。

#### C. `*.json` (元数据 / Metadata)
这是数据的“身份证”或“说明书”。
*   **含义**：键值对格式的文本文件。
*   **内容**：记录了扫描仪的硬件参数（如 `RepetitionTime (TR)` 扫描一张图几秒、`Manufacturer` 机器型号）。
*   **继承原则**：根目录下的 JSON（如 `task-perception_bold.json`）适用于所有受试者；文件夹里的 JSON 只适用于该文件夹。

### 3. 纵向实验设计：从 Session 看懂流程
进入 `sub-01` 文件夹，我们看到的不仅是文件，而是**实验的时间轴**。通过 `ses-` (Session) 文件夹的区分，我们可以复盘整个实验过程：

*   **阶段一：`ses-anatomy` (结构扫描)**
    *   **任务**：受试者躺着不动。
    *   **产出**：只有 `anat/` 文件夹，里面是 `T1w` 图像。这是为了获得受试者的高清大脑3D模型，作为后续功能的底板。

*   **阶段二：`ses-perceptionTraining` (感知训练)**
    *   **任务**：观看大量图片进行机器学习模型的训练数据采集。
    *   **产出**：`func/` 文件夹下有大量的 `run-01` 到 `run-10`，数据量最大。

*   **阶段三：`ses-perceptionTest` (感知测试)**
    *   **任务**：正式测试阶段，记录受试者看图时的脑反应。

*   **阶段四：`ses-imageryTest` (想象测试)**
    *   **关键差异**：任务名变为了 `task-imagery`。受试者不再看图，而是闭眼想象之前看过的图片。
    *   **分析价值**：对比“看图”和“想象”在同一个大脑区域（如 ROI Mask 定义的区域）的信号差异，是这个数据集的核心研究点。

### 4. 微观命名解码：文件名即数据库
以 `sub-01_ses-imageryTest01_task-imagery_run-01_bold_preproc.nii.gz` 为例，这是一个信息密度极高的文件名：

| 字段 (Key) | 值 (Value) | 含义 |
| :--- | :--- | :--- |
| **sub** | 01 | **Who:** 1号受试者 |
| **ses** | imageryTest01 | **When:** 想象力测试阶段 |
| **task** | imagery | **What:** 正在做想象任务 |
| **run** | 01 | **Count:** 第1次重复 |
| **Suffix** | bold | **Type:** 血氧水平依赖信号 (功能像) |
| **Desc** | preproc | **Status:** 已经过预处理 |

### 5. 本案例总结
GOD 数据集展示了**“多阶段、多任务、多模态”**的复杂实验如何被井井有条地管理。阅读此类数据集时，**先看 Session (阶段)，再看 Task (任务)，最后找对应的 ROI (掩膜)。**

---
## 四、 通用解法：Python 自动化目录爬取工具

当数据集包含数百个文件夹时，手动点击查看不仅慢，而且容易遗漏细节。我们使用 Python 脚本来实现**“结构透视”**。

此脚本的核心功能是** “智能折叠”**：它会自动识别重复的模式（如 `sub-01`, `sub-02` ... `sub-50`），只展开第一个样本作为代表，将其余的折叠起来。这让你能在一屏内看清整个数据集的逻辑骨架。

### 1. 工具代码 (`tree_view.py`)
将以下代码复制并保存为 `.py` 文件，修改底部的 `target_path` 即可运行。

```python
import os
import re
from pathlib import Path

def print_tree(
    root_path: str,
    prefix: str = "",
    collapse_threshold: int = 2,  # 超过2个相似项就折叠
    ignore_hidden: bool = True    # 隐藏 .git 等文件
):
    path_obj = Path(root_path)
    if not path_obj.exists():
        print(f"路径不存在: {root_path}")
        return

    # 获取并排序文件
    try:
        items = sorted([p for p in path_obj.iterdir()])
    except PermissionError:
        print(f"{prefix}[权限被拒绝]")
        return

    if ignore_hidden:
        items = [i for i in items if not i.name.startswith('.')]

    # --- 核心算法：正则分组 ---
    # 将 sub-01, sub-02 统一泛化为 sub-{N} 模式
    grouped_items = {}
    for item in items:
        # 使用正则将文件名中的数字替换为占位符
        pattern = re.sub(r'\d+', '{N}', item.name)
        if pattern not in grouped_items:
            grouped_items[pattern] = []
        grouped_items[pattern].append(item)

    pattern_keys = list(grouped_items.keys())
    
    # 遍历打印
    for i, pattern in enumerate(pattern_keys):
        group = grouped_items[pattern]
        is_last_group = (i == len(pattern_keys) - 1)
        
        # 树枝符号
        connector = "└── " if is_last_group else "├── "
        child_prefix = "    " if is_last_group else "│   "

        # 1. 始终展示这一组的第一个项目 (Representative)
        first_item = group[0]
        print(f"{prefix}{connector}{first_item.name}")

        # 2. 如果是文件夹，递归深入 (只深入第一个，避免冗余)
        if first_item.is_dir():
            print_tree(first_item, prefix + child_prefix, collapse_threshold, ignore_hidden)

        # 3. 如果这一组有多个相似项，打印折叠信息
        if len(group) > 1:
            fold_connector = "    " if is_last_group else "│   "
            remaining_count = len(group) - 1
            if remaining_count > 0:
                print(f"{prefix}{fold_connector}└── ... [已自动折叠 {remaining_count} 个相似项: 结尾是 {group[-1].name}]")

# --- 使用入口 ---
if __name__ == "__main__":
    # 将此处修改为你要分析的数据集路径
    # Windows用户请注意使用 r"" 防止转义，例如 r"D:\Data\GOD"
    target_path = r"D:\Datasets\GOD_Dataset_Root" 
    
    print(f"Dataset Structure: {os.path.basename(target_path)}")
    print_tree(target_path)
```

### 2. 输出结果解读
运行上述代码后，你将获得如下清晰的视图。请注意看脚本是如何帮你“划重点”的：

```text
Dataset Structure: GOD
├── derivatives
│   └── preproc-spm
│       └── output
│           └── sub-01  <-- 【重点】脚本只展开了 sub-01，让你看清内部结构
│               ├── ses-anatomy
│               │   └── ...
│               ├── ses-imageryTest01
│               │   └── ...
│           └── ... [已自动折叠 4 个相似项: 结尾是 sub-05] <-- 【重点】sub-02到05被自动折叠，避免刷屏
├── sub-01
│   ├── ses-anatomy
│   └── ...
└── ...
```

**结论：** 只要看懂了这个脚本输出的结构图，结合前文的命名规范分析，你就能在5分钟内掌握任何陌生数据集的使用方法。