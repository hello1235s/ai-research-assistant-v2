# 数据分析与可视化方法

## 1. 描述性统计

### 集中趋势度量
- **均值（Mean）**：所有数据的算术平均值，对异常值敏感
- **中位数（Median）**：排序后位于中间位置的值，对异常值稳健
- **众数（Mode）**：出现频率最高的值

### 离散程度度量
- **方差（Variance）**：数据与均值之差的平方的平均值
- **标准差（Standard Deviation）**：方差的平方根，常用σ表示
- **极差（Range）**：最大值与最小值之差
- **四分位距（IQR）**：Q3 - Q1，衡量中间50%数据的离散程度
- **变异系数（CV）**：标准差与均值之比，用于比较不同量纲数据的离散程度

### 分布特征度量
- **偏度（Skewness）**：分布不对称程度的度量
  - 偏度 > 0：右偏（正偏）
  - 偏度 < 0：左偏（负偏）
  - 偏度 = 0：对称分布
- **峰度（Kurtosis）**：分布尾部厚度和峰尖程度的度量

## 2. 数据可视化方法

### 2.1 单变量可视化

**直方图（Histogram）**
- 用途：展示连续变量的分布情况
- 适用场景：了解数据分布形态、发现异常值
- 关键参数：bin数量（通常用Sturges公式或Scott规则）

**箱线图（Box Plot）**
- 用途：展示数据的五数概括（最小值、Q1、中位数、Q3、最大值）
- 适用场景：比较多个组的分布、识别异常值
- 关键要素：箱体（IQR）、 whisker（1.5×IQR）、异常点

**密度图（Density Plot）**
- 用途：平滑估计概率密度函数
- 适用场景：比较多个分布的形状

### 2.2 双变量可视化

**散点图（Scatter Plot）**
- 用途：展示两个连续变量的关系
- 适用场景：发现相关性、识别聚类模式
- 增强技巧：添加回归线、按类别着色

**折线图（Line Plot）**
- 用途：展示变量随时间/顺序的变化趋势
- 适用场景：时间序列分析、趋势展示

**柱状图（Bar Chart）**
- 用途：比较不同类别的数值大小
- 适用场景：分类数据比较、频率统计

**热力图（Heatmap）**
- 用途：展示矩阵数据的值分布
- 适用场景：相关性矩阵、混淆矩阵

### 2.3 多变量可视化

**散点图矩阵（Pair Plot）**
- 用途：展示多个变量两两之间的关系
- 适用场景：探索多变量数据的相关性

**平行坐标图（Parallel Coordinates）**
- 用途：展示高维数据的模式
- 适用场景：多变量分类、聚类分析

**雷达图（Radar Chart）**
- 用途：展示多个维度的性能指标
- 适用场景：多维评估、能力对比

## 3. 统计推断基础

### 假设检验
- **原假设（H₀）**：需要被检验的假设
- **备择假设（H₁）**：与原假设对立的假设
- **p值**：在原假设为真时，观察到当前或更极端结果的概率
- **显著性水平（α）**：通常取0.05或0.01

### 常用检验方法
- **t检验**：比较两组均值差异
- **方差分析（ANOVA）**：比较多组均值差异
- **卡方检验**：检验分类变量的独立性
- **相关性检验**：Pearson、Spearman、Kendall

## 4. Matplotlib绘图基础

### 基本图表创建
```python
import matplotlib.pyplot as plt
import numpy as np

# 基本线图
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.figure(figsize=(10, 6))
plt.plot(x, y, label='sin(x)', color='blue', linewidth=2)
plt.xlabel('x轴')
plt.ylabel('y轴')
plt.title('正弦函数')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

### 常用图表类型
```python
# 散点图
plt.scatter(x, y, c=colors, s=sizes, alpha=0.6, cmap='viridis')
plt.colorbar(label='颜色说明')

# 柱状图
plt.bar(categories, values, color='skyblue', edgecolor='black')

# 直方图
plt.hist(data, bins=20, color='green', alpha=0.7, edgecolor='black')

# 箱线图
plt.boxplot([data1, data2], labels=['组1', '组2'])

# 子图
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes[0, 0].plot(x, y)
axes[0, 1].scatter(x, y)
axes[1, 0].hist(data)
axes[1, 1].bar(categories, values)
```

## 5. Plotly交互式可视化

### 基本用法
```python
import plotly.express as px
import plotly.graph_objects as go

# 散点图
fig = px.scatter(df, x='x_col', y='y_col', color='category', 
                 size='size_col', hover_data=['extra_col'])
fig.update_layout(title='交互式散点图', width=800, height=600)
fig.show()

# 热力图
fig = px.imshow(correlation_matrix, text_auto=True, aspect="auto")
fig.show()
```

## 6. Seaborn统计可视化

```python
import seaborn as sns

# 设置样式
sns.set_style('whitegrid')
sns.set_palette('husl')

# 箱线图
sns.boxplot(data=df, x='category', y='value')

# 小提琴图
sns.violinplot(data=df, x='category', y='value')

# 回归图
sns.regplot(data=df, x='x', y='y')

# 热力图
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)

# 分布图
sns.histplot(data=df, x='value', kde=True, hue='category')
```
