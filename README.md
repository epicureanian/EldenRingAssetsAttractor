# 艾尔登法环资产提取项目

# 主要功能简述
艾尔登法环游戏中含有很多模型资产，这些资产现在应景被解包并存储在本地，但是为了导入这些资产到其他软件仍然需要一些其他的工具进行解压缩，项目的目的是自动化工具解压缩资产的流程，涉及到命令行工具调用、修改文件路径等操作

# 文件路径
在本地艾尔登法环游戏根目录是：E:\SteamLibrary\steamapps\common\ELDEN RING\Game
在这个目录所有的写操作都要获得许可，不允许擅自改变这个文件夹中的内容，并且工作时主要使用的文件夹为：asset\、map\

# 主要工具
## WitchyBND
路径为：E:\Program\AssetProjects\WitchyBND-v3.0.0.1-win-x64\WitchyBND.exe，使用方法为
WitchyBND <输入文件> 
后面的输入文件可以有多个，但是目前没尝试过太多的，考虑到电脑内存可能不要超过10个
命令主要用于解压.matbin文件为.matbin.xml文件，之后可以从.matbin.xml文件中读取到材质贴图路径、参数等信息

## AquaTools中的SoulsModelTool
路径为：E:\Program\AssetProjects\AquaToolset\net9.0-windows7.0\SoulsModelTool.exe，使用方法为
SoulsModelTool <输入文件> 
后面的输入文件可以有多个，但是目前没尝试过太多的，考虑到电脑内存可能不要超过10个
命令主要用于将.dcx文件解压出.fbx文件，这一过程中还会解压出.matData.json，这一文件用于锁定贴图文件
