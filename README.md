# TOEFL iBT Writing Practice Simulator

실제 TOEFL iBT Writing 시험 화면을 모방한 데스크톱 연습 애플리케이션입니다.  
Python 내장 라이브러리(`tkinter`)만 사용하여 별도 설치 없이 가볍게 실행됩니다.

---

## 📸 화면 구성

```
┌─────────────────────────────────────────────────────────────┐
│  TOEFL iBT®   [▶ 시작] [⏹ 정지] [↺ 초기화]  00:00   [📂 불러오기] [💾 저장] │
├─────────────────────────────────────────────────────────────┤
│  단어 수  0 words   │  Ctrl+휠: 글씨 크기 조절             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   (글쓰기 영역 — Times New Roman 12pt)                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ 주요 기능

| 기능 | 설명 |
|---|---|
| ⏱ **카운트업 타이머** | 0초부터 시작 / 시작·정지·초기화 버튼 |
| 📊 **실시간 단어 수** | 서브바에 항상 표시, 100/150단어 기준 색상 변화 |
| 🔤 **글씨 크기 조절** | `Ctrl + 마우스휠`로 8~36pt 실시간 조절 |
| 🚫 **부정행위 방지** | `Ctrl+C/V/X`, 마우스 우클릭 차단 |
| 📂 **불러오기** | 이전 저장 파일을 자동 탐색하여 목록으로 표시 |
| 💾 **스마트 저장** | 첫 줄이 `Dear`/`To`로 시작하면 `essay/email/`, 나머지는 `essay/academic/`에 자동 분류 저장 |

---

## 🗂 저장 폴더 구조

```
실행 파일 위치/
└── essay/
    ├── email/          ← Dear, To 로 시작하는 글
    │   └── 20260704_200000.txt
    └── academic/       ← 일반 Academic Discussion
        └── 20260704_201500.txt
```

저장 파일에는 저장 시각, 경과 시간, 단어 수 메타데이터가 함께 기록됩니다.

---

## 🚀 실행 방법

### 방법 1 — Python 스크립트로 직접 실행

```bash
# Python 3.8 이상 필요 (tkinter 내장)
python toefl_simulator.py
```

### 방법 2 — 단독 실행 파일(.exe) 빌드 (Windows)

```bash
# PyInstaller 설치
pip install pyinstaller

# 빌드 (현재 폴더에 dist/TOEFL_Writing_Simulator.exe 생성)
pyinstaller --onefile --windowed --name "TOEFL_Writing_Simulator" toefl_simulator.py
```

> **Anaconda 환경 사용 시**
> ```bash
> conda activate <환경명>
> pip install pyinstaller
> pyinstaller --onefile --windowed --name "TOEFL_Writing_Simulator" toefl_simulator.py
> ```

---

## 📋 요구 사항

- Python **3.8** 이상
- 외부 라이브러리 없음 (`tkinter`, `os`, `sys`, `datetime` 모두 내장)

---

## 📁 프로젝트 구조

```
writingtool/
├── toefl_simulator.py   # 메인 애플리케이션 (단일 파일)
├── README.md
├── .gitignore
└── LICENSE
```

---

## 📝 License

[MIT License](LICENSE)
