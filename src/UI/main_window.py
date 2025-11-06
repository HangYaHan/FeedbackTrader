from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quant Trading System")
        self.setGeometry(100, 100, 800, 600)  # 设置窗口位置和大小

        # 添加更多的 UI 元素和逻辑

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())