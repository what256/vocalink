# animation.py  – minimal, centred 7-bar sound overlay  ─────────
# pip install pyside6 pyaudio

import math, sys, time, array, threading, ctypes, signal
import pyaudio
from   PySide6.QtCore    import Qt, QTimer, QRectF, QPoint
from   PySide6.QtGui     import QColor, QPainter, QGuiApplication
from   PySide6.QtWidgets import QApplication, QWidget

# ── tunables ───────────────────────────────────────────────────
PILL_W , PILL_H = 170, 38        # overall pill size
CORNER_R        = 19
BAR_W           = 4
N_BARS          = 9              # exactly seven bars
GAP             = 6              # tight gap between bars
FPS             = 30
X_SHIFT         = 40             # slight right shift
OFFSET_TASK     = 10             # distance from task-bar
MIC_CHUNK_MS    = 40
# colours
BG      = QColor(35, 38, 42)
RING    = QColor(69, 89,120,200)
BAR_CLR = QColor(255,255,255)
# ───────────────────────────────────────────────────────────────

def _enable_win_blur(hwnd: int):
    """Enable Acrylic-like blur on Windows 10/11."""
    try:
        accent  = ctypes.c_int(4)     # ACCENT_ENABLE_BLURBEHIND
        class ACCENTPOLICY(ctypes.Structure):
            _fields_= [("AccentState", ctypes.c_int),
                        ("AccentFlags", ctypes.c_int),
                        ("GradientColor", ctypes.c_int),
                        ("AnimationId", ctypes.c_int)]
        data = ACCENTPOLICY(accent,0,0,0)
        ctypes.windll.user32.SetWindowCompositionAttribute(
            ctypes.c_void_p(hwnd), ctypes.pointer(ctypes.c_int(19)),
            ctypes.byref(data), ctypes.sizeof(data))
    except Exception:
        pass

class MicSampler(threading.Thread):
    """Background thread that continuously measures mic RMS level."""
    def __init__(self):
        super().__init__(daemon=True)
        self.level  = 0.0
        self.running= True
        pa          = pyaudio.PyAudio()
        self.chunk  = int(16000*MIC_CHUNK_MS/1000)
        self.stream = pa.open(format=pyaudio.paInt16, channels=1,
                              rate=16000, input=True,
                              frames_per_buffer=self.chunk)
    def run(self):
        while self.running:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            ints = array.array('h', data)
            rms  = math.sqrt(sum(i*i for i in ints)/len(ints))
            self.level = min(rms/6000, 1.0)
    def stop(self):
        self.running = False
        self.stream.close()

class RecordingOverlay(QWidget):
    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint |
                               Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(PILL_W, PILL_H)

        # center bottom + slight right shift
        scr = QGuiApplication.primaryScreen().availableGeometry()
        self.move((scr.width()-PILL_W)//2 + X_SHIFT,
                  scr.height()-PILL_H-OFFSET_TASK)
        if sys.platform.startswith("win"):
            _enable_win_blur(int(self.winId()))

        self._t0  = time.time()
        self.mic  = MicSampler(); self.mic.start()
        self.tmr  = QTimer(self, timeout=self.update, interval=1000//FPS)
        self.tmr.start()
        signal.signal(signal.SIGINT, lambda *_: self.close())

    # ---------- painting ----------------------------------------------------
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # outer ring
        p.setPen(Qt.NoPen); p.setBrush(RING)
        p.drawRoundedRect(QRectF(0,0,PILL_W,PILL_H), CORNER_R, CORNER_R)

        # inner pill
        p.setBrush(BG)
        p.drawRoundedRect(QRectF(2,2,PILL_W-4,PILL_H-4), CORNER_R-2, CORNER_R-2)

        # compute centred starting x for bars
        total_w = N_BARS*BAR_W + (N_BARS-1)*GAP
        start_x = (PILL_W - total_w)/2
        base_y  = PILL_H/2
        level   = self.mic.level
        t       = time.time()-self._t0

        p.setBrush(BAR_CLR)
        for i in range(N_BARS):
            phase = t*3 + i*0.9
            h     = 4 + (level*18)*abs(math.sin(phase))
            y     = base_y - h/2
            x     = start_x + i*(BAR_W+GAP)
            p.drawRoundedRect(QRectF(x, y, BAR_W, h), 2, 2)
        p.end()

    def closeEvent(self, e):
        self.tmr.stop(); self.mic.stop()
        QApplication.quit(); e.accept()

# ---------------- entry-point ---------------------------------------------
if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    RecordingOverlay().show()
    sys.exit(app.exec())
