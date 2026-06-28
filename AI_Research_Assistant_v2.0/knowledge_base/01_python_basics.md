# Python编程基础与进阶

## 1. Python基础语法

### 变量与数据类型
Python是动态类型语言，无需显式声明变量类型。
```python
# 基本数据类型
integer = 10          # 整数
floating = 3.14       # 浮点数
string = "Hello"      # 字符串
boolean = True        # 布尔值
list_data = [1, 2, 3] # 列表
dict_data = {"a": 1}  # 字典
```

### 控制流程
```python
# 条件语句
if condition:
    pass
elif condition2:
    pass
else:
    pass

# 循环
for i in range(10):
    pass

while condition:
    pass
```

## 2. 函数与模块

### 函数定义
```python
def my_function(param1, param2="default"):
    """函数文档字符串"""
    return param1 + param2
```

### 常用内置模块
- `os` - 操作系统接口
- `sys` - 系统相关参数
- `datetime` - 日期和时间处理
- `json` - JSON数据处理
- `re` - 正则表达式
- `math` / `statistics` - 数学和统计函数

## 3. NumPy基础

### 数组创建
```python
import numpy as np

arr = np.array([1, 2, 3])          # 一维数组
arr2d = np.array([[1, 2], [3, 4]]) # 二维数组
zeros = np.zeros((3, 3))            # 全零数组
ones = np.ones((3, 3))              # 全一数组
arange = np.arange(0, 10, 2)      # 等差数组
linspace = np.linspace(0, 1, 100)  # 等分数组
```

### 常用操作
```python
arr.shape        # 数组形状
arr.dtype        # 数据类型
arr.reshape(2, 3) # 重塑形状
arr.sum()        # 求和
arr.mean()       # 均值
arr.std()        # 标准差
arr.max()        # 最大值
arr.min()        # 最小值
np.dot(a, b)     # 矩阵乘法
```

## 4. Pandas数据处理

### 数据结构
```python
import pandas as pd

# Series - 一维数据
s = pd.Series([1, 2, 3], index=['a', 'b', 'c'])

# DataFrame - 二维数据
df = pd.DataFrame({
    'column1': [1, 2, 3],
    'column2': ['a', 'b', 'c']
})
```

### 数据操作
```python
# 读取数据
df = pd.read_csv('data.csv')
df = pd.read_excel('data.xlsx')
df = pd.read_json('data.json')

# 基本操作
df.head()          # 前5行
df.tail()          # 后5行
df.info()          # 数据信息
df.describe()      # 统计描述
df.shape           # 数据形状

# 筛选数据
df[df['column'] > 10]  # 条件筛选
df.loc[row, col]        # 按标签定位
df.iloc[row, col]       # 按位置定位

# 数据处理
df.dropna()        # 删除缺失值
df.fillna(0)       # 填充缺失值
df.groupby('col')  # 分组
df.sort_values('col')  # 排序
```

## 5. 常用科研编程技巧

### 文件操作
```python
# 读取文本文件
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 写入文件
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write(content)
```

### 错误处理
```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("除零错误")
except Exception as e:
    print(f"其他错误: {e}")
finally:
    print("清理操作")
```

### 列表推导式
```python
# 基本形式
squares = [x**2 for x in range(10)]

# 带条件
evens = [x for x in range(10) if x % 2 == 0]
```
