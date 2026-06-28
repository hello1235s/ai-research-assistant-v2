# 机器学习基础算法

## 1. 机器学习概述

### 机器学习类型
- **监督学习**：使用带标签的数据进行训练（分类、回归）
- **无监督学习**：使用无标签数据进行训练（聚类、降维）
- **强化学习**：通过与环境交互学习最优策略

### 机器学习流程
1. 数据收集与预处理
2. 特征工程
3. 模型选择
4. 模型训练
5. 模型评估
6. 模型优化
7. 模型部署

## 2. 数据预处理

### 缺失值处理
```python
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer

# 删除缺失值
df.dropna(inplace=True)

# 均值填充
imputer = SimpleImputer(strategy='mean')
df_filled = imputer.fit_transform(df)

# 中位数填充
imputer = SimpleImputer(strategy='median')
df_filled = imputer.fit_transform(df)

# 众数填充
imputer = SimpleImputer(strategy='most_frequent')
df_filled = imputer.fit_transform(df)
```

### 特征缩放
```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# 标准化（Z-score标准化）
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 归一化（Min-Max缩放）
scaler = MinMaxScaler()
X_normalized = scaler.fit_transform(X)
```

### 类别编码
```python
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

# 标签编码
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# 独热编码
encoder = OneHotEncoder(sparse=False)
X_encoded = encoder.fit_transform(X_cat)
```

## 3. 回归算法

### 线性回归
```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# 评估
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
```

### 多项式回归
```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('poly', PolynomialFeatures(degree=2)),
    ('linear', LinearRegression())
])
pipeline.fit(X_train, y_train)
```

### 正则化回归
```python
from sklearn.linear_model import Ridge, Lasso, ElasticNet

# Ridge回归（L2正则化）
ridge = Ridge(alpha=1.0)
ridge.fit(X_train, y_train)

# Lasso回归（L1正则化）
lasso = Lasso(alpha=1.0)
lasso.fit(X_train, y_train)

# ElasticNet（L1+L2）
elastic = ElasticNet(alpha=1.0, l1_ratio=0.5)
elastic.fit(X_train, y_train)
```

## 4. 分类算法

### 逻辑回归
```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

model = LogisticRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# 评估
accuracy = accuracy_score(y_test, y_pred)
print(classification_report(y_test, y_pred))
```

### 决策树
```python
from sklearn.tree import DecisionTreeClassifier, plot_tree

model = DecisionTreeClassifier(max_depth=5, min_samples_split=10)
model.fit(X_train, y_train)

# 可视化
plt.figure(figsize=(20, 10))
plot_tree(model, feature_names=feature_names, class_names=class_names, filled=True)
plt.show()
```

### 随机森林
```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100, max_depth=10)
model.fit(X_train, y_train)

# 特征重要性
importances = model.feature_importances_
```

### 支持向量机
```python
from sklearn.svm import SVC

model = SVC(kernel='rbf', C=1.0, gamma='scale')
model.fit(X_train, y_train)
```

### K近邻
```python
from sklearn.neighbors import KNeighborsClassifier

model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train, y_train)
```

## 5. 聚类算法

### K-Means聚类
```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

model = KMeans(n_clusters=3, random_state=42)
labels = model.fit_predict(X)

# 评估
silhouette = silhouette_score(X, labels)

# 肘部法则确定K值
inertias = []
for k in range(2, 10):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X)
    inertias.append(kmeans.inertia_)
```

### 层次聚类
```python
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage

model = AgglomerativeClustering(n_clusters=3)
labels = model.fit_predict(X)

# 树状图
linked = linkage(X, method='ward')
dendrogram(linked, orientation='top')
plt.show()
```

## 6. 模型评估与选择

### 交叉验证
```python
from sklearn.model_selection import cross_val_score, KFold, StratifiedKFold

# K折交叉验证
scores = cross_val_score(model, X, y, cv=5)
print(f"交叉验证分数: {scores.mean():.4f} (+/- {scores.std():.4f})")
```

### 网格搜索
```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15]
}
grid_search = GridSearchCV(RandomForestClassifier(), param_grid, cv=5)
grid_search.fit(X_train, y_train)
print(f"最优参数: {grid_search.best_params_}")
```

### 评估指标

**分类问题**
- 准确率（Accuracy）
- 精确率（Precision）
- 召回率（Recall）
- F1分数
- ROC-AUC
- 混淆矩阵

**回归问题**
- 均方误差（MSE）
- 均方根误差（RMSE）
- 平均绝对误差（MAE）
- R²决定系数
- 调整R²

## 7. 模型保存与加载
```python
import pickle
import joblib

# 保存模型
joblib.dump(model, 'model.pkl')

# 加载模型
model = joblib.load('model.pkl')
```
