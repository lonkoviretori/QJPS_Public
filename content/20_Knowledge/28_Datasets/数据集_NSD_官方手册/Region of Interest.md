---
publish: true
---

这是为你整理的 **NSD 数据集笔记 Part 8**。

在脑机接口（BCI）和神经解码研究中，**[[ROI]] (Region of Interest)** 是你最重要的“特征选择”工具。全脑有数万个体素，直接全扔进模型里通常全是噪声。你需要告诉模型：“只看处理视觉的 V1 区”或者“只看处理人脸的 FFA 区”。

这份笔记将帮你搞清楚 NSD 提供了哪些 ROI，以及如何读取它们。

---

### 📝 [NSD 数据集] 笔记 Part 8：感兴趣区域 (ROIs) 与特征掩膜
**标签：** #FeatureSelection #VisualCortex #V1-V4 #FFA/PPA

#### 1. ROI 的两大阵营 (Categories)

NSD 提供了两种来源的 ROI，解码时主要用**手动绘制**的那部分，因为更贴合被试个体。

**A. 视觉皮层 - 视网膜拓扑 (Retinotopic / Low-level)**
*   **文件前缀：** `prf-visualrois`
*   **包含区域：** `V1v`, `V1d`, `V2v`, `V2d`, `V3v`, `V3d`, `hV4`。
*   **用途：** 解码**低级视觉特征**（如边缘、纹理、方向）。如果你想重构图像的像素（Image Reconstruction），这些是核心区域。
*   **变体：** `prf-eccrois` 按**偏心率**（离视野中心多远）划分。
    *   `ecc0pt5`: 视野中心 0.5°（精细视觉）。
    *   `ecc4+`: 视野外围（周边视觉）。

**B. 功能定位 - 语义类别 (Functional / High-level)**
*   **文件前缀：** `floc-faces` (人脸), `floc-places` (场景), `floc-words` (文字), `floc-bodies` (身体)。
*   **包含区域：**
    *   **Faces:** `FFA` (Fusiform Face Area), `OFA`.
    *   **Places:** `PPA` (Parahippocampal Place Area), `RSC`, `OPA`.
    *   **Bodies:** `EBA`, `FBA`.
    *   **Words:** `VWFA` (Visual Word Form Area).
*   **用途：** 解码**语义类别**（如“这是一张人脸还是房子？”）。
*   **⚠️ 注意：** 这里的 ROI 划定标准比较**宽松 (Liberal)** (t > 0)，这意味着 ROI 面积可能很大。为了提高信噪比，你在分析时可能需要根据 t值 进一步筛选最活跃的前 N 个体素。

**C. 通用视觉区 (The "Kitchen Sink")**
*   **名称：** `nsdgeneral`
*   **内容：** 作者手动圈定的、对实验刺激有反应的**整个后部视觉皮层**。
*   **用途：** 如果你不想纠结选 V1 还是 FFA，直接用这个。它包含了绝大部分有用的视觉信号。

#### 2. 文件位置与格式 (File Locations)

你需要下载和你的 Betas 空间一致的 ROI 文件。通常是 `func1pt8mm`。

*   **路径示例：**
    `nsddata/ppdata/subj01/func1pt8mm/roi/prf-visualrois.nii.gz`
*   **文件内容：**
    这是一个与 fMRI 数据形状相同的 3D 矩阵。
    *   `0`: 背景（不属于该 ROI）。
    *   `1, 2, 3...`: 整数标签，代表具体的子区域（如 1=V1v, 2=V1d...）。
    *   `-1`: 非皮层区域（在 Volume 格式中）。

#### 3. 标签映射表 (Lookup Table) —— 关键！

拿到 `.nii.gz` 里的整数 `1` 或 `2`，怎么知道它代表 V1 还是 V2？
**必须查阅配套的 `.mgz.ctab` 或 `.mgz.txt` 文件**，或者直接看文档说明。

**常用映射速查 (根据文档整理)：**

*   **`prf-visualrois`**:
    *   通常顺序是：V1v, V1d, V2v, V2d, V3v, V3d, hV4 (具体需核对 `.ctab` 文件，不同被试可能只有 label ID 不同，但通常是顺序排列)。
*   **`floc-faces`**:
    *   OFA, FFA-1, FFA-2, mTL-faces, aTL-faces。
*   **`floc-places`**:
    *   OPA, PPA, RSC。

#### 4. 代码实战：如何提取 V1 区的信号 (Python)

这是解码任务中最常用的操作：**Masking**。

```python
import nibabel as nib
import numpy as np

# 1. 加载 ROI 掩膜 (Mask)
roi_path = 'nsddata/ppdata/subj01/func1pt8mm/roi/prf-visualrois.nii.gz'
roi_img = nib.load(roi_path)
roi_data = roi_img.get_fdata() # Shape: (81, 104, 83)

# 2. 查表得知 V1 对应的标签
# 假设查阅 .ctab 后知道: V1v=1, V1d=2. 我们想把这两个合并成完整的 V1
v1_mask_bool = (roi_data == 1) | (roi_data == 2)

# 3. 加载 Betas (大脑激活图)
# 假设已经加载好了 betas, Shape: (81, 104, 83, 750)
# betas = load_betas(...) 

# 4. 提取特征 (Masking)
# 利用 boolean索引，直接提取 V1 区域的所有体素
# 结果 Shape: (V1_voxel_count, 750)
v1_betas = betas[v1_mask_bool, :] 

print(f"全脑体素: {betas.shape[0]*betas.shape[1]*betas.shape[2]}")
print(f"V1区体素: {v1_betas.shape[0]}")
# 现在你可以把 v1_betas 转置成 (750, N) 喂给 SVM 或 线性回归了
```

#### 5. 其他高级 ROI (了解即可)

*   **Atlases (Kastner2015, HCP_MMP1):** 基于群体平均的地图。不如手动绘制的准，除非该被试的数据质量太差画不出 ROI。
*   **Streams:** 视觉流（腹侧流/背侧流）。做宏观网络分析用的。
*   **Thalamus / MTL:** 丘脑和海马。涉及视觉记忆或注意力的研究会用到。

---

### 🎓 研一新生避坑指南

1.  **左右半脑 (lh/rh) vs 合并版:**
    *   文件夹里通常有 `lh.prf-visualrois.nii.gz` (左半球) 和 `prf-visualrois.nii.gz` (双侧合并)。
    *   **建议：** 直接用**双侧合并版**（文件名不带 lh/rh 的），除非你专门研究半球偏侧化。

2.  **ROI 的重叠问题:**
    *   不同的 ROI 文件之间可能会有重叠。例如 `nsdgeneral` 包含了 `V1`。
    *   但是，**同一个 ROI 文件内部**（如 `prf-visualrois`）的标签是互斥的（一个体素要么是 V1，要么是 V2，不会既是 V1 又是 V2）。

3.  **数据稀疏性:**
    *   提取完 ROI 后，记得检查一下。有些边缘区域的 ROI 可能会因为跑出扫描视野而全是 0。

至此，你已经拥有了处理 NSD 数据集的全套工具箱：**下载数据 -> 读取 Betas -> 加载 ROI -> 提取特征**。下一步就是要把提取出来的矩阵塞进机器学习模型里了！