---
publish: true
---

**全称：** Neuroimaging Informatics Technology Initiative
**地位：** 神经影像领域的 `JPG` 或 `MP3`，是绝对的标准格式。

#### 特点：
1.  **自带空间坐标 (Affine Matrix)：**
    这是 NIfTI 的灵魂。它不仅存了 3D 矩阵数据，还存了一个 4x4 的矩阵（Affine），告诉计算机这个 3D 矩阵怎么映射到真实世界。
    *   *比如：* `(100, 100, 50)` 这个体素点，在真实大脑里是左脑还是右脑？由 NIfTI 头文件决定。
2.  **压缩格式 (`.gz`)：**
    `.nii` 是原始文件，`.gz` 代表用 Gzip 压缩过。就像 `.tar.gz` 一样。
3.  **兼容性极强：**
    所有的医学看图软件（ITK-SNAP, MRIcron, FSL, SPM）都能直接打开它。

#### 缺点：
*   **读取慢：** 因为是压缩包，想读最后一个数据点，往往需要把整个文件解压进内存。
*   **不适合大数据集训练：** 如果你有 1000 个 `.nii.gz` 文件，每次训练都要反复解压读取，I/O 效率极低。

#### 🐍 Python 读取方式 (使用 `nibabel` 库)
```python
import nibabel as nib

# 加载文件 (此时只读了头文件，没占太大内存)
img = nib.load('brain.nii.gz')

# 1. 获取 3D/4D 数据矩阵 (这一步会把数据解压加载到内存，可能很大)
data = img.get_fdata() 
print(data.shape)  # 输出比如 (81, 104, 83)

# 2. 获取空间坐标矩阵 (重要！)
affine = img.affine
print(affine)
# 用途：如果你要把结果画回大脑里，保存新文件时必须把这个 affine 塞回去
```

---
