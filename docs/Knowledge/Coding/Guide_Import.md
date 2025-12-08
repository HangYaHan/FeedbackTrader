Python 包管理与多级导入（结合本项目实践）

- Beruto 项目使用 `src` 目录作为包根，下面总结最小可行的规则与示例，帮助避免多级导入踩坑。

快速结论（TL;DR）
- 目录里有 `__init__.py` 才是包；`src`、`src/system`、`src/data` 等都要有。我们已经有。
- 跨包导入用绝对路径：`from src.system.log import get_logger`。
- 同包内部用相对导入：`from .log import get_logger`（见 `src/system/CLI.py`）。
- 运行入口用模块形式：`python -m src.main` 或 `python -m src.system.CLI`，避免手动改 `sys.path`。
- 不要使用 `from ... import *`；用明确的名字，必要时在 `__init__.py` 中维护 `__all__`。

项目结构（局部）
```
src/
        __init__.py          <- 标记包根
        system/
                __init__.py
                log.py
                CLI.py
        backtest/
                __init__.py
                engine.py
        strategy/
                __init__.py
                MovingAverage.py
        data/
                __init__.py
                fetcher.py
                adapters/
                        __init__.py
                        akshare_adapter.py
        main.py
```

本项目中的导入示例
- 同包相对导入：`src/system/CLI.py` → `from .log import get_logger`
- 跨包绝对导入：`src/backtest/engine.py` → `from src.system.log import get_logger`
- 入口模块确保路径：`src/main.py` 在直接运行时将项目根加入 `sys.path`，随后使用 `from src.system.CLI import main as cli_main`
- 其他跨包示例：`src/strategy/yahan_strategies.py` → `from src.strategy.calc_lines import CLOSE, MA`

推荐运行方式（避免找不到包）
```bash
# 从仓库根目录执行
python -m src.main            # 主入口
python -m src.system.CLI      # 直接启动交互 CLI
```

为什么要用绝对导入（跨包）
- 清晰：一眼知道从哪来，避免同名模块遮蔽。
- 稳定：与当前工作目录无关（只要以包方式运行）。
- IDE/类型检查友好：更好地解析跳转。

为什么要用相对导入（同包）
- 重构友好：包名变化时，兄弟模块互相引用不受影响。
- 降低循环导入风险：在需要时可局部延迟导入（如 `src/system/CLI.py` 在函数内导入 `src.backtest.engine`）。

关于 `__init__.py`
- 作用：告诉解释器“这里是包”。无此文件时，目录不会被当作包，绝对/相对导入都会失败。
- 本项目的根：`src/__init__.py` 很简洁，仅标记包并可选维护 `__all__`。
- 可选用途：在子包 `__init__.py` 中集中导出公共接口（例如 `from .log import get_logger`），便于调用端写 `from src.system import get_logger`。

常见错误与排查
- `ModuleNotFoundError: No module named 'src'`
        - 确认在仓库根执行：`python -m src.main`；不要在 `src/` 里直接 `python main.py`。
        - 确认 `src` 目录下有 `__init__.py`（已存在）。
- 相对导入失败：`ImportError: attempted relative import with no known parent package`
        - 用模块方式运行：`python -m src.system.CLI`，不要用 `python CLI.py`。
- 循环导入：把相互依赖的导入移到函数内部延迟执行，或拆分公共逻辑到新模块。

写新模块的简单约定
- 在新目录下放 `__init__.py`，再写模块文件。
- 跨包引用用绝对导入：`from src.<package>.<module> import Foo`。
- 同包引用用相对导入：`from .bar import Baz`。
- 如需对外暴露统一接口，在包的 `__init__.py` 里维护 `__all__` 或显式导入。

参考：Python 搜索路径
- 解释器查找顺序：当前工作目录 → `PYTHONPATH` → 标准库 → site-packages → `.pth` 中的路径。
- 用 `python -m` 运行包模块，可以避免手动修改 `sys.path`。
>>> from fibo import *
