---
publish: true
---

**标签：** #fMRI #Visual-Decoding #Large-Scale #Generative-AI #BCI

## 1. 基本信息 (Metadata)
*   **全称：** Natural Scenes Dataset
*   **发布年份：** 2021 (Data Paper) / 2022 (Full Access)
*   **来源/论文：** Allen et al., *Nature Neuroscience* (2021) [https://www.nature.com/articles/s41593-021-00962-x]
*   **下载地址：** AWS S3 (`s3://natural-scenes-dataset`)
*   **被试数量：** 8名 (Subj01-Subj08)
*   **文件格式：**
    *   **[[hdf5]]** (推荐，适合 Python 读取)
    *   **[[nii.gz]]** (NIfTI，通用脑影像格式)
*   **数据量级：** 极为庞大 (全量 >10TB，核心Betas约 500GB)。

## 2. 实验设计 (Experimental Design)
*   **任务：** 连续再认任务 (Continuous Recognition Task) —— 观看自然图像，按键判断“这张图之前是否见过”。
*   **图片来源：** MS COCO (Common Objects in Context) 2017 数据集。
	*   **数量：** 共 **73,000 张** (从 COCO 中精选出的)。
	*   **图像预处理：**
	    *   **裁剪 (Cropping):** 原始 COCO 图片是长方形的，但实验需要正方形。作者使用了一套算法（基于 Object Loss）进行裁剪，优先保留图片中心和关键物体（如人脸）。
	    *   **尺寸：** 425 x 425 像素。
		    *   **背景：** 灰色背景 (RGB: 127, 127, 127)。
	*   **Shared(共享组):**
	    *   有 **1,000 张** 特定的图片，**所有 8 名被试**都看过。
	*   **Unique(独有组):**
	    *   每名被试还看了额外的 **9,000 张** 图片，这些图片互相之间几乎不重叠。
*   **Trial 结构：**
    *   **呈现图片：** 3 秒 (3000 ms)
    *   **间隔 (Gap)：** 1 秒 (1000 ms)
    *   **重复次数：** 每张图在整个实验周期中重复看 **3次**。
*   **Session设置：** 每人扫描了 **30-40 个 Session** (耗时整整一年)，每个 Session 包含 12 个 Runs，每个 Run 包含 75 个 Trials。

## 3. 硬件与信号 (Signal Specs)
*   **设备：** 7T (7 Tesla) 超高场 fMRI 扫描仪。
*   **信号类型：** BOLD (血氧水平依赖信号)。
*   **分辨率 (重要)：**
    *   **空间：** 1.8mm 各向同性 (Standard) 或 1mm (High-res)。**解码推荐用 1.8mm。**
    *   **时间 (TR)：** 原始采样 1.6s，但 Betas 版本已重采样至 **1.333s** (针对1.8mm版本)。
*   **预处理状态：** 推荐使用 **Betas (b3版本)**。
    *   包含操作：拟合 HRF (Fit HRF) + GLMdenoise (去噪) + Ridge Regression (岭回归)。
    *   **注意：** 没有做高通滤波，也没有转换单位（见下文代码坑点）。

## 4. 关键代码片段 (Snippets)
*   *如何读取数据：* `h5py.File('betas_session01.hdf5', 'r')`
*   *⭐ 必须做的数值修正：*
    ```python
    # 文档明确指出：数据被乘了300并存为int16
    betas_real = betas_int16.astype(float) / 300.0
    ```
*   *标签对齐逻辑：*
    需要联合 `nsd_expdesign.mat` (获取 73k-ID) 和 `nsd_stimuli.hdf5` (获取图片像素) 来构建 (X, Y)。

## 5. 现有 SOTA 性能 (Benchmarks)
*   **Reconstruction (重建):** 
*   **Identification (识别):** 


## 6. 个人备注/坑点 (Pitfalls)


## 7.根据数据集提出科学问题
1. 同一张图片，不同人看得到的脑信号的对比。
2. 
3. 同一张图片，同一个人在不同时间看，得到的脑信号对比。（根据某一次脑信号，检索另外两次的脑信号）
4. 结构或语义相似的图片，得到的脑信号的对比。
5. 不同图片，人看到时关注点的区别（复杂背景和简单背景）
6. 数据是如何处理的？进行了哪些处理？
