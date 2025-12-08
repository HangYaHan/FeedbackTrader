# Quickstart

1) 安装 Python 3.12+（确保已加入 PATH）。
2) 克隆仓库：
```powershell
git clone https://github.com/HangYaHan/Beruto.git
cd Beruto
```
3) 创建并初始化虚拟环境（自动创建 `.venv` 并安装 `requirements.txt`）：
```powershell
./create_venv.ps1
```
   若被执行策略阻止，可临时放开：
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force; ./create_venv.ps1
```
4) 激活虚拟环境（后续命令需在激活状态下执行）：
```powershell
.\.venv\Scripts\Activate.ps1
```
5) 运行主程序：
```powershell
python -m src.main
```
6) 退出虚拟环境（可选）：
```powershell
deactivate
```