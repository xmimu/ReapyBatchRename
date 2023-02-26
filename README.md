# ReapyBatchRename

代码地址：https://github.com/xmimu/ReapyBatchRename.git



### 使用：

- ​	0、python 3.9 以上环境、正确安装并配置好 reapy

- ​	1、pip install -r requirements.txt 安装依赖库

- ​	1、打开reaper、然后在外部运行 ReapyBatchRename.py

- ​	2、如果需要，可以用 pyinstaller 打包 exe 大概27mb（不过你都装python了

  

### 基本功能：

- ​	0、支持 轨道、区域、midi 和媒体对象、标记 的改名

- ​	1、支持 过滤仅选择的对应资源，但是暂不支持选中的 区域、标记

- ​	2、支持 区分大小写、全字匹配、正则表达式 三种匹配模式

- ​	3、支持 手动多行输入，比如从表格复制多行字符，点表格编辑，自动换行输入

- ​	4、支持 撤销



### 已知问题：

- 更新 区域、标记的时候，dock 窗口不正常刷新，但是名称已正确修改

- midi 和 媒体对象 改名操作无法撤销

  

### 后续实现：

- ​	1、正则表达式 group 替换

- ​	2、类似 REAPER 通配符风格的替换
