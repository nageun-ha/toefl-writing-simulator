"""
TOEFL iBT Writing Practice Simulator  v3
==========================================
- 좌측 패널 제거 → 전체 화면 글쓰기 영역
- 타이머: 0초부터 카운트업, [시작] [정지] [초기화] 버튼
- Ctrl+마우스휠로 글씨 크기 조절
- [불러오기] → 저장 폴더 자동 탐색 커스텀 목록 창
- 단어 수: 서브바에 상시 크게 표시
- 저장 위치: exe 위치 기준 ./essay/email/ 또는 ./essay/academic/
"""

import tkinter as tk
from tkinter import messagebox, font as tkfont
import os
import sys
import datetime

# ── exe/스크립트 기준 저장 경로 ────────────────────────────────────────────
if getattr(sys, "frozen", False):          # PyInstaller 번들 실행 시
    BASE_DIR = os.path.dirname(sys.executable)
else:                                       # 스크립트 직접 실행 시
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── 색상 상수 ──────────────────────────────────────────────────────────────
HEADER_BG          = "#1B3A6B"
HEADER_FG          = "#FFFFFF"
BTN_TIMER_BG       = "#2E5FA3"
BTN_TIMER_ACTIVE   = "#3D74C7"
BTN_STOP_BG        = "#7B3F00"
BTN_STOP_ACTIVE    = "#A0522D"
BTN_RESET_BG       = "#3A3A3A"
BTN_RESET_ACTIVE   = "#555555"
BTN_LOAD_BG        = "#1A5276"
BTN_LOAD_ACTIVE    = "#2471A3"
BTN_SAVE_BG        = "#1E6B2E"
BTN_SAVE_ACTIVE    = "#27A642"

TIMER_NORMAL       = "#FFFFFF"
TIMER_RUNNING      = "#90EE90"   # 실행 중 연두색
TIMER_STOPPED      = "#FFD700"   # 정지 중 노란색

TEXTAREA_BG        = "#FFFFFF"
TEXTAREA_FG        = "#111111"
BOTTOM_BAR_BG      = "#F0F0F0"
WORDCOUNT_FG       = "#333333"

FONT_SIZE_MIN      = 8
FONT_SIZE_MAX      = 36
FONT_SIZE_DEFAULT  = 12


class TOEFLSimulator:
    """TOEFL iBT Writing Practice Simulator 메인 클래스 (v2)."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("TOEFL iBT Writing Practice Simulator")
        self.root.configure(bg=HEADER_BG)

        # ── 상태 변수 ──
        self.timer_seconds  = 0
        self.timer_running  = False
        self._after_id      = None
        self.font_size      = FONT_SIZE_DEFAULT

        # ── 창 설정 ──
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        w, h   = min(1100, sw - 80), min(750, sh - 80)
        root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        root.minsize(700, 480)

        self._setup_fonts()
        self._setup_ui()
        self._bind_events()

    # ══════════════════════════════════════════════════════════════════════
    # 폰트
    # ══════════════════════════════════════════════════════════════════════
    def _setup_fonts(self):
        self.font_logo      = tkfont.Font(family="Arial", size=15, weight="bold")
        self.font_ibt       = tkfont.Font(family="Arial", size=12, weight="bold")
        self.font_timer     = tkfont.Font(family="Courier New", size=22, weight="bold")
        self.font_btn       = tkfont.Font(family="Arial", size=9,  weight="bold")
        self.font_textarea  = tkfont.Font(family="Times New Roman", size=self.font_size)
        self.font_bottom    = tkfont.Font(family="Arial", size=10)
        self.font_wc_big    = tkfont.Font(family="Arial", size=13, weight="bold")  # 단어수 강조

    # ══════════════════════════════════════════════════════════════════════
    # UI 구성
    # ══════════════════════════════════════════════════════════════════════
    def _setup_ui(self):
        self._setup_header()
        tk.Frame(self.root, bg="#0D2347", height=2).pack(fill=tk.X)
        self._setup_wordcount_bar()   # ← 단어 수 전용 서브바
        tk.Frame(self.root, bg="#D0D0D0", height=1).pack(fill=tk.X)
        self._setup_body()

    # ── 헤더 ──────────────────────────────────────────────────────────────
    def _setup_header(self):
        hdr = tk.Frame(self.root, bg=HEADER_BG, height=60)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        # ── 좌: 로고 ──
        logo_f = tk.Frame(hdr, bg=HEADER_BG)
        logo_f.pack(side=tk.LEFT, padx=20)
        tk.Label(logo_f, text="TOEFL", font=self.font_logo,
                 fg="#FFD700", bg=HEADER_BG).pack(side=tk.LEFT)
        tk.Label(logo_f, text=" iBT®", font=self.font_ibt,
                 fg=HEADER_FG, bg=HEADER_BG).pack(side=tk.LEFT)

        # ── 우: [불러오기] + [저장] ──
        right_f = tk.Frame(hdr, bg=HEADER_BG)
        right_f.pack(side=tk.RIGHT, padx=18)

        self._mk_btn(right_f, "💾  저장", BTN_SAVE_BG, BTN_SAVE_ACTIVE,
                     self.save_response).pack(side=tk.RIGHT, padx=(4, 0))
        self._mk_btn(right_f, "📂  불러오기", BTN_LOAD_BG, BTN_LOAD_ACTIVE,
                     self.load_file).pack(side=tk.RIGHT, padx=(4, 4))

        # ── 중앙: 타이머 컨트롤 ──
        center_f = tk.Frame(hdr, bg=HEADER_BG)
        center_f.pack(side=tk.LEFT, expand=True)

        timer_row = tk.Frame(center_f, bg=HEADER_BG)
        timer_row.pack(expand=True)

        # [▶ 시작]
        self.btn_start = self._mk_btn(timer_row, "▶  시작",
                                      BTN_TIMER_BG, BTN_TIMER_ACTIVE,
                                      self.start_timer)
        self.btn_start.pack(side=tk.LEFT, padx=(0, 6))

        # [⏹ 정지]
        self.btn_stop = self._mk_btn(timer_row, "⏹  정지",
                                     BTN_STOP_BG, BTN_STOP_ACTIVE,
                                     self.stop_timer)
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 6))
        self.btn_stop.config(state=tk.DISABLED, bg="#555555")

        # 타이머 표시
        self.lbl_timer = tk.Label(
            timer_row, text="00:00",
            font=self.font_timer, fg=TIMER_NORMAL, bg=HEADER_BG, width=6)
        self.lbl_timer.pack(side=tk.LEFT, padx=(4, 6))

        # [↺ 초기화]
        self.btn_reset = self._mk_btn(timer_row, "↺  초기화",
                                      BTN_RESET_BG, BTN_RESET_ACTIVE,
                                      self.reset_timer)
        self.btn_reset.pack(side=tk.LEFT, padx=(0, 0))

    def _mk_btn(self, parent, text, bg, active_bg, cmd):
        """버튼 공통 팩토리."""
        return tk.Button(
            parent, text=text, font=self.font_btn,
            bg=bg, fg=HEADER_FG,
            activebackground=active_bg, activeforeground=HEADER_FG,
            relief=tk.FLAT, padx=12, pady=5,
            cursor="hand2", command=cmd,
        )

    # ── 단어 수 서브바 ─────────────────────────────────────────────────────
    def _setup_wordcount_bar(self):
        """헤더 바로 아래 상시 표시되는 단어 수 바."""
        self.wc_bar = tk.Frame(self.root, bg="#EEF2F8", height=36)
        self.wc_bar.pack(fill=tk.X)
        self.wc_bar.pack_propagate(False)

        tk.Label(
            self.wc_bar,
            text="단어 수",
            font=self.font_bottom,
            fg="#6A7FA8",
            bg="#EEF2F8",
            padx=18,
        ).pack(side=tk.LEFT, fill=tk.Y)

        self.lbl_wc_big = tk.Label(
            self.wc_bar,
            text="0",
            font=self.font_wc_big,
            fg="#1B3A6B",
            bg="#EEF2F8",
        )
        self.lbl_wc_big.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(
            self.wc_bar,
            text="words",
            font=self.font_bottom,
            fg="#6A7FA8",
            bg="#EEF2F8",
            padx=4,
        ).pack(side=tk.LEFT, fill=tk.Y)

        self.lbl_hint = tk.Label(
            self.wc_bar,
            text="Ctrl+휠: 글씨 크기 조절",
            font=self.font_bottom,
            fg="#AAAAAA",
            bg="#EEF2F8",
            padx=20,
        )
        self.lbl_hint.pack(side=tk.LEFT, fill=tk.Y)

    # ── 바디 (글쓰기 영역) ────────────────────────────────────────────────
    def _setup_body(self):
        body = tk.Frame(self.root, bg=TEXTAREA_BG)
        body.pack(fill=tk.BOTH, expand=True)

        # 텍스트 영역
        ta_frame = tk.Frame(body, bg=TEXTAREA_BG, padx=16, pady=12)
        ta_frame.pack(fill=tk.BOTH, expand=True)

        vsb = tk.Scrollbar(ta_frame, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area = tk.Text(
            ta_frame,
            font=self.font_textarea,
            bg=TEXTAREA_BG, fg=TEXTAREA_FG,
            insertbackground="#1B3A6B",
            relief=tk.FLAT, bd=0,
            wrap=tk.WORD,
            yscrollcommand=vsb.set,
            padx=20, pady=16,
            spacing2=3, spacing3=5,
            undo=True,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.text_area.yview)

        # 하단 상태바
        bar = tk.Frame(self.root, bg=BOTTOM_BAR_BG, height=28)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        self.lbl_save_info = tk.Label(
            bar, text="",
            font=self.font_bottom, fg="#3A7D44", bg=BOTTOM_BAR_BG,
            anchor="w", padx=16)
        self.lbl_save_info.pack(side=tk.LEFT, expand=True, fill=tk.Y)

    # ══════════════════════════════════════════════════════════════════════
    # 이벤트 바인딩
    # ══════════════════════════════════════════════════════════════════════
    def _bind_events(self):
        # 단어 수
        self.text_area.bind("<KeyRelease>", self.update_word_count)

        # Ctrl+마우스휠 → 글씨 크기
        self.text_area.bind("<Control-MouseWheel>", self._on_ctrl_wheel)

        # 복사/붙여넣기 차단
        for seq in ("<Control-c>", "<Control-v>", "<Control-x>",
                    "<Command-c>", "<Command-v>", "<Command-x>"):
            self.text_area.bind(seq, lambda e: "break")

        # 우클릭 차단
        self.text_area.bind("<Button-3>", lambda e: "break")

        # 포커스
        self.text_area.focus_set()

    # ══════════════════════════════════════════════════════════════════════
    # 글씨 크기 조절
    # ══════════════════════════════════════════════════════════════════════
    def _on_ctrl_wheel(self, event):
        if event.delta > 0:
            self.font_size = min(self.font_size + 1, FONT_SIZE_MAX)
        else:
            self.font_size = max(self.font_size - 1, FONT_SIZE_MIN)
        self.font_textarea.config(size=self.font_size)
        self.lbl_hint.config(
            text=f"글씨 크기: {self.font_size}pt  (Ctrl+휠로 조절)")
        return "break"   # 기본 스크롤 방지

    # ══════════════════════════════════════════════════════════════════════
    # 타이머 (카운트업)
    # ══════════════════════════════════════════════════════════════════════
    def start_timer(self):
        if self.timer_running:
            return
        self.timer_running = True
        self.btn_start.config(state=tk.DISABLED, bg="#555555")
        self.btn_stop.config(state=tk.NORMAL,    bg=BTN_STOP_BG)
        self.lbl_timer.config(fg=TIMER_RUNNING)
        self._tick()

    def _tick(self):
        if not self.timer_running:
            return
        self.timer_seconds += 1
        m, s = divmod(self.timer_seconds, 60)
        self.lbl_timer.config(text=f"{m:02d}:{s:02d}")
        self._after_id = self.root.after(1000, self._tick)

    def stop_timer(self):
        """타이머 일시정지."""
        if not self.timer_running:
            return
        self.timer_running = False
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        self.btn_start.config(state=tk.NORMAL, bg=BTN_TIMER_BG)
        self.btn_stop.config(state=tk.DISABLED, bg="#555555")
        self.lbl_timer.config(fg=TIMER_STOPPED)

    def reset_timer(self):
        """타이머 초기화 (정지 후 00:00 리셋)."""
        self.stop_timer()
        self.timer_seconds = 0
        self.lbl_timer.config(text="00:00", fg=TIMER_NORMAL)
        self.btn_start.config(state=tk.NORMAL, bg=BTN_TIMER_BG)
        self.btn_stop.config(state=tk.DISABLED, bg="#555555")

    # ══════════════════════════════════════════════════════════════════════
    # 단어 수
    # ══════════════════════════════════════════════════════════════════════
    def update_word_count(self, event=None):
        content = self.text_area.get("1.0", tk.END).strip()
        count = len(content.split()) if content else 0
        # 서브바의 큰 숫자 업데이트
        self.lbl_wc_big.config(text=str(count))
        # 100단어 이상이면 파란색 강조, 150 이상이면 초록
        if count >= 150:
            self.lbl_wc_big.config(fg="#1E6B2E")
        elif count >= 100:
            self.lbl_wc_big.config(fg="#1B3A6B")
        else:
            self.lbl_wc_big.config(fg="#9B1C1C" if count > 0 else "#1B3A6B")

    # ══════════════════════════════════════════════════════════════════════
    # 불러오기
    # ══════════════════════════════════════════════════════════════════════
    def load_file(self):
        """저장 폴더를 자동 탐색하여 파일 목록 창을 띄웁니다."""
        # essay/academic, essay/email 에서 .txt 파일 수집
        essay_dir = os.path.join(BASE_DIR, "essay")
        entries = []   # (표시 이름, 전체 경로)
        for folder_name in ("academic", "email"):
            folder_path = os.path.join(essay_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue
            for fname in sorted(os.listdir(folder_path), reverse=True):
                if not fname.lower().endswith(".txt"):
                    continue
                fpath = os.path.join(folder_path, fname)
                # 메타: Words 줄 파싱
                meta = ""
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.startswith("Words"):
                                meta = line.strip()
                                break
                except Exception:
                    pass
                label = f"[{folder_name}]  {fname}    {meta}"
                entries.append((label, fpath))

        if not entries:
            messagebox.showinfo(
                "불러오기",
                "저장된 파일이 없습니다.\n\n"
                f"저장 위치: {BASE_DIR}\n"
                "(글을 작성하고 [저장] 버튼을 누르면 파일이 생성됩니다.)",
                parent=self.root,
            )
            return

        self._show_file_picker(entries)

    def _show_file_picker(self, entries):
        """저장 파일 목록을 보여주는 커스텀 Toplevel 창."""
        dlg = tk.Toplevel(self.root)
        dlg.title("이전 저장 파일 불러오기")
        dlg.configure(bg="#F8F9FB")
        dlg.resizable(True, True)

        # 창 크기 및 위치
        dw, dh = 720, 420
        px = self.root.winfo_x() + (self.root.winfo_width()  - dw) // 2
        py = self.root.winfo_y() + (self.root.winfo_height() - dh) // 2
        dlg.geometry(f"{dw}x{dh}+{px}+{py}")
        dlg.minsize(500, 300)
        dlg.grab_set()   # 모달

        # 제목
        tk.Label(
            dlg,
            text="불러올 파일을 선택하세요",
            font=tkfont.Font(family="Arial", size=12, weight="bold"),
            fg="#1B3A6B", bg="#F8F9FB",
            anchor="w", padx=16, pady=10,
        ).pack(fill=tk.X)
        tk.Frame(dlg, bg="#1B3A6B", height=2).pack(fill=tk.X)

        # 리스트박스 + 스크롤바
        list_frame = tk.Frame(dlg, bg="#F8F9FB", padx=12, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)

        sb = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        lb = tk.Listbox(
            list_frame,
            font=tkfont.Font(family="Courier New", size=10),
            bg="#FFFFFF", fg="#111111",
            selectbackground="#1B3A6B", selectforeground="#FFFFFF",
            relief=tk.FLAT, bd=0,
            activestyle="none",
            yscrollcommand=sb.set,
        )
        lb.pack(fill=tk.BOTH, expand=True)
        sb.config(command=lb.yview)

        for label, _ in entries:
            lb.insert(tk.END, "  " + label)

        lb.selection_set(0)   # 첫 항목 기본 선택

        # 버튼 영역
        btn_frame = tk.Frame(dlg, bg="#EBEBEB", height=50)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        btn_frame.pack_propagate(False)

        def do_load():
            sel = lb.curselection()
            if not sel:
                return
            _, fpath = entries[sel[0]]
            dlg.destroy()
            self._load_from_path(fpath)

        tk.Button(
            btn_frame, text="불러오기",
            font=tkfont.Font(family="Arial", size=10, weight="bold"),
            bg=BTN_LOAD_BG, fg="#FFFFFF",
            activebackground=BTN_LOAD_ACTIVE, activeforeground="#FFFFFF",
            relief=tk.FLAT, padx=20, pady=8,
            cursor="hand2", command=do_load,
        ).pack(side=tk.RIGHT, padx=12, pady=8)

        tk.Button(
            btn_frame, text="취소",
            font=tkfont.Font(family="Arial", size=10),
            bg="#888888", fg="#FFFFFF",
            activebackground="#AAAAAA", activeforeground="#FFFFFF",
            relief=tk.FLAT, padx=20, pady=8,
            cursor="hand2", command=dlg.destroy,
        ).pack(side=tk.RIGHT, padx=(0, 4), pady=8)

        # 더블클릭으로도 불러오기
        lb.bind("<Double-Button-1>", lambda e: do_load())

    def _load_from_path(self, filepath):
        """지정 경로의 파일을 텍스트 영역에 로드합니다."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                raw = f.read()
        except (IOError, UnicodeDecodeError) as e:
            messagebox.showerror("불러오기 오류",
                                 f"파일을 열 수 없습니다:\n{e}", parent=self.root)
            return

        sep = "=" * 60 + "\n\n"
        content = raw.split(sep, 1)[-1] if sep in raw else raw

        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, content)
        self.update_word_count()

        short = os.path.basename(filepath)
        self.lbl_save_info.config(text=f"📂 불러옴: {short}", fg="#1A5276")

    # ══════════════════════════════════════════════════════════════════════
    # 저장
    # ══════════════════════════════════════════════════════════════════════
    def save_response(self):
        content = self.text_area.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning(
                "저장 실패", "⚠️ 작성된 내용이 없습니다.\n내용을 입력한 후 저장해주세요.",
                parent=self.root)
            return

        # 저장 디렉토리 결정 (essay/email 또는 essay/academic)
        essay_dir  = os.path.join(BASE_DIR, "essay")
        first_line = content.split("\n")[0].strip().lower()
        if first_line.startswith(("dear", "to ")):
            save_dir  = os.path.join(essay_dir, "email")
            category  = "essay/email"
        else:
            save_dir  = os.path.join(essay_dir, "academic")
            category  = "essay/academic"

        try:
            os.makedirs(save_dir, exist_ok=True)
        except OSError as e:
            messagebox.showerror("저장 오류",
                                 f"폴더를 만들 수 없습니다:\n{e}", parent=self.root)
            return

        # 파일명 생성
        ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ts}.txt"
        filepath = os.path.join(save_dir, filename)

        # 타이머 기록
        m, s      = divmod(self.timer_seconds, 60)
        elapsed   = f"{m:02d}:{s:02d}"
        wc        = len(content.split())

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("TOEFL iBT Writing Practice\n")
                f.write(f"Saved  : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Elapsed: {elapsed}\n")
                f.write(f"Words  : {wc}\n")
                f.write("=" * 60 + "\n\n")
                f.write(content)
        except IOError as e:
            messagebox.showerror("저장 오류",
                                 f"파일을 저장할 수 없습니다:\n{e}", parent=self.root)
            return

        short = os.path.join(".", category, filename)
        self.lbl_save_info.config(
            text=f"✔ 저장 완료 → {short}", fg="#3A7D44")

        messagebox.showinfo(
            "저장 완료",
            f"✅ 저장 완료!\n\n"
            f"📁 {short}\n"
            f"⏱  경과 시간: {elapsed}\n"
            f"📝 단어 수: {wc}",
            parent=self.root,
        )


# ══════════════════════════════════════════════════════════════════════════
# 진입점
# ══════════════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    TOEFLSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
