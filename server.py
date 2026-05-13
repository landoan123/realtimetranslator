# ============================================================
# server.py -- Voice Translator Server (Hybrid: Local + Online)
# Chay: python server.py
# Truy cap: http://localhost:5000
# ============================================================
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import re, os, json, threading, urllib.request, urllib.parse

app = Flask(__name__, static_folder=".")
CORS(app)

# ============================================================
# TỪ ĐIỂN SONG NGỮ — dùng để dịch cực nhanh offline
# ============================================================

DICTIONARIES = {
    "vi-en": {
        "xin chào": "hello", "chào": "hello", "tạm biệt": "goodbye",
        "cảm ơn": "thank you", "không có gì": "you're welcome",
        "xin lỗi": "sorry", "vâng": "yes", "có": "yes", "không": "no",
        "làm ơn": "please", "dạ": "yes", "thưa": "dear",
        "tôi": "I", "bạn": "you", "anh": "he", "chị": "she",
        "chúng tôi": "we", "họ": "they", "nó": "it",
        "là": "is", "có thể": "can", "muốn": "want", "cần": "need",
        "đi": "go", "đến": "come", "làm": "do", "nói": "say",
        "biết": "know", "thấy": "see", "nghe": "hear",
        "hiểu": "understand", "đồng ý": "agree", "không đồng ý": "disagree",
        "hội nghị": "conference", "cuộc họp": "meeting",
        "thảo luận": "discussion", "báo cáo": "report",
        "trình bày": "presentation", "đề xuất": "proposal",
        "dự án": "project", "kế hoạch": "plan", "mục tiêu": "objective",
        "kết quả": "result", "vấn đề": "issue", "giải pháp": "solution",
        "chương trình": "agenda", "biên bản": "minutes",
        "người phát biểu": "speaker", "người tham dự": "attendee",
        "chủ tọa": "chairperson", "diễn giả": "presenter",
        "câu hỏi": "question", "trả lời": "answer",
        "tổng kết": "summary", "kết luận": "conclusion",
        "quyết định": "decision", "đề nghị": "motion",
        "bỏ phiếu": "vote", "phê duyệt": "approval",
        "ngân sách": "budget", "chi phí": "cost",
        "doanh thu": "revenue", "lợi nhuận": "profit",
        "hợp đồng": "contract", "thỏa thuận": "agreement",
        "đối tác": "partner", "khách hàng": "customer",
        "hôm nay": "today", "ngày mai": "tomorrow", "hôm qua": "yesterday",
        "bây giờ": "now", "sau": "later", "sớm": "soon",
        "tốt": "good", "tốt hơn": "better", "tốt nhất": "best",
        "quan trọng": "important", "cần thiết": "necessary",
        "mới": "new", "cũ": "old", "lớn": "large", "nhỏ": "small",
        "nhanh": "fast", "chậm": "slow", "khó": "difficult", "dễ": "easy",
        "đúng": "correct", "sai": "wrong",
        "một": "one", "hai": "two", "ba": "three", "bốn": "four",
        "năm": "five", "sáu": "six", "bảy": "seven", "tám": "eight",
        "chín": "nine", "mười": "ten",
        "phòng họp": "meeting room", "văn phòng": "office",
        "công ty": "company", "tổ chức": "organization",
    },
    "en-vi": {
        "hello": "xin chào", "hi": "xin chào", "goodbye": "tạm biệt",
        "bye": "tạm biệt", "thank you": "cảm ơn", "thanks": "cảm ơn",
        "sorry": "xin lỗi", "yes": "vâng", "no": "không", "please": "làm ơn",
        "welcome": "chào mừng", "dear": "kính thưa",
        "i": "tôi", "you": "bạn", "he": "anh ấy", "she": "chị ấy",
        "we": "chúng tôi", "they": "họ", "it": "nó",
        "is": "là", "are": "là", "was": "là", "can": "có thể",
        "want": "muốn", "need": "cần", "go": "đi", "come": "đến",
        "do": "làm", "say": "nói", "know": "biết", "see": "thấy",
        "hear": "nghe", "understand": "hiểu", "agree": "đồng ý",
        "have": "có", "will": "sẽ", "should": "nên", "must": "phải",
        "conference": "hội nghị", "meeting": "cuộc họp",
        "discussion": "thảo luận", "report": "báo cáo",
        "presentation": "trình bày", "proposal": "đề xuất",
        "project": "dự án", "plan": "kế hoạch", "objective": "mục tiêu",
        "result": "kết quả", "issue": "vấn đề", "solution": "giải pháp",
        "agenda": "chương trình nghị sự", "minutes": "biên bản họp",
        "speaker": "diễn giả", "attendee": "người tham dự",
        "chairperson": "chủ tọa", "presenter": "người trình bày",
        "question": "câu hỏi", "answer": "câu trả lời",
        "summary": "tóm tắt", "conclusion": "kết luận",
        "decision": "quyết định", "budget": "ngân sách", "cost": "chi phí",
        "revenue": "doanh thu", "profit": "lợi nhuận",
        "contract": "hợp đồng", "agreement": "thỏa thuận",
        "partner": "đối tác", "customer": "khách hàng",
        "team": "nhóm", "department": "phòng ban",
        "manager": "quản lý", "director": "giám đốc",
        "today": "hôm nay", "tomorrow": "ngày mai", "yesterday": "hôm qua",
        "now": "bây giờ", "later": "sau này", "soon": "sớm thôi",
        "morning": "buổi sáng", "afternoon": "buổi chiều", "evening": "buổi tối",
        "good": "tốt", "better": "tốt hơn", "best": "tốt nhất",
        "important": "quan trọng", "necessary": "cần thiết",
        "new": "mới", "old": "cũ", "large": "lớn", "small": "nhỏ",
        "fast": "nhanh", "slow": "chậm", "difficult": "khó", "easy": "dễ",
        "correct": "đúng", "wrong": "sai", "great": "tuyệt vời",
        "one": "một", "two": "hai", "three": "ba", "four": "bốn",
        "five": "năm", "six": "sáu", "seven": "bảy", "eight": "tám",
        "nine": "chín", "ten": "mười",
        "the": "", "a": "", "an": "", "this": "này", "that": "đó",
        "office": "văn phòng", "company": "công ty",
        "organization": "tổ chức", "room": "phòng",
    },
    "en-ja": {
        "hello": "こんにちは", "goodbye": "さようなら", "thank you": "ありがとう",
        "yes": "はい", "no": "いいえ", "please": "お願いします",
        "meeting": "会議", "conference": "カンファレンス",
        "report": "レポート", "project": "プロジェクト",
        "good": "良い", "bad": "悪い", "today": "今日", "tomorrow": "明日",
        "question": "質問", "answer": "答え", "understand": "わかります",
        "important": "重要", "plan": "計画",
    },
    "en-ko": {
        "hello": "안녕하세요", "goodbye": "안녕히 가세요", "thank you": "감사합니다",
        "yes": "네", "no": "아니요", "please": "부탁합니다",
        "meeting": "회의", "conference": "컨퍼런스",
        "report": "보고서", "project": "프로젝트",
        "good": "좋다", "bad": "나쁘다", "today": "오늘", "tomorrow": "내일",
        "important": "중요한", "plan": "계획",
    },
    "en-zh": {
        "hello": "你好", "goodbye": "再见", "thank you": "谢谢",
        "yes": "是的", "no": "不", "please": "请",
        "meeting": "会议", "conference": "会议",
        "report": "报告", "project": "项目", "plan": "计划",
        "good": "好", "bad": "坏", "today": "今天", "tomorrow": "明天",
        "question": "问题", "answer": "回答", "important": "重要",
    },
    "en-fr": {
        "hello": "bonjour", "goodbye": "au revoir", "thank you": "merci",
        "yes": "oui", "no": "non", "please": "s'il vous plaît",
        "meeting": "réunion", "conference": "conférence",
        "report": "rapport", "project": "projet", "plan": "plan",
        "good": "bon", "bad": "mauvais", "today": "aujourd'hui",
        "tomorrow": "demain", "question": "question", "answer": "réponse",
        "important": "important",
    },
    "en-de": {
        "hello": "hallo", "goodbye": "auf Wiedersehen", "thank you": "danke",
        "yes": "ja", "no": "nein", "please": "bitte",
        "meeting": "Treffen", "conference": "Konferenz",
        "report": "Bericht", "project": "Projekt", "plan": "Plan",
        "good": "gut", "bad": "schlecht", "today": "heute", "tomorrow": "morgen",
        "important": "wichtig",
    },
}


# ============================================================
# LOGIC DỊCH DICTIONARY
# ============================================================

def translate_phrase(text, direction):
    dictionary = DICTIONARIES.get(direction, {})
    if not dictionary:
        src, tgt = direction.split("-") if "-" in direction else ("en", "vi")
        fallback = f"en-{tgt}" if src != "en" else f"en-vi"
        dictionary = DICTIONARIES.get(fallback, {})

    text_lower = text.lower().strip()
    words = text_lower.split()
    result_tokens = []
    i = 0
    while i < len(words):
        matched = False
        for length in range(min(5, len(words) - i), 0, -1):
            phrase = " ".join(words[i:i + length])
            clean_phrase = phrase.rstrip(".,!?;:")
            if clean_phrase in dictionary:
                translated = dictionary[clean_phrase]
                if translated:
                    result_tokens.append(translated)
                i += length
                matched = True
                break
        if not matched:
            word = words[i]
            clean = word.rstrip(".,!?;:")
            if clean not in ["the", "a", "an"]:
                result_tokens.append(clean)
            i += 1
    return " ".join(result_tokens)


# ============================================================
# VIET NAME DETECTION
# ============================================================
import unicodedata as _ud

VIET_SURNAMES = set([
    'nguyen','tran','le','pham','hoang','huynh','phan','vu','vo',
    'dang','bui','do','ho','ngo','duong','ly','dinh','truong',
    'doan','vuong','lam','luu','dao','mai','to','thai',
    'quach','chu','lieu','trinh','ta','tong','cao','dam','tang',
    'nghiem','than','tieu','mac','luong','kieu','van',
    # co dau
    'nguyễn','trần','lê','phạm','hoàng','huỳnh',
    'vũ','võ','đặng','bùi','đỗ','hồ','ngô',
    'dương','lý','đinh','trương','đoàn',
    'vương','lâm','lưu','đào','tô','hà',
    'thái','quách','liêu','trịnh','tạ','tống',
    'đàm','tăng','nghiêm','thân',
])

VIET_STOPWORDS = set([
    'là','và','của','cho','với','từ','đến','tại','ở','về',
    'không','có','được','này','đó','khi','sau','trong',
    'ngoài','vì','nên','nhưng','mà','thì','bởi','do',
    'tôi','bạn','anh','chị','em','ông','bà','cô',
    'mọi','các','những','một','hai','ba',
    'trường','đại','học','thành','phố',
    'xã','nhân','văn','khoa','tất','cả',
    'xin','chào','năm','ngày','tháng',
    'sinh','viên','giáo','viên','bác','sĩ','kỹ','sư',
    'công','ty','tổ','chức','hội','nghị','đoàn','thể',
    'tên','họ','tuổi','quê',
    # khong dau
    'sinh','vien','giao','bac','si','ky',
    'cong','ty','to','chuc','hoi','nghi','doan','the',
    'ten','ho','tuoi','que','truong','dai','hoc',
    'is','a','an','the','and','from','of','to','in','at',
])


def _no_accent(s):
    return ''.join(c for c in _ud.normalize('NFD', s)
                   if _ud.category(c) != 'Mn')

def capitalize_viet_names(text):
    """Viet hoa ho ten Viet de Google khong dich sai."""
    words = text.split()
    result = list(words)
    i = 0
    while i < len(words):
        w_clean = re.sub(r'[.,!?;:]', '', words[i]).lower()
        w_norm  = _no_accent(w_clean)
        if w_clean in VIET_SURNAMES or w_norm in VIET_SURNAMES:
            result[i] = words[i][0].upper() + words[i][1:]
            j = i + 1
            count = 0
            while j < len(words) and count < 4:
                nxt = re.sub(r'[.,!?;:]', '', words[j]).lower()
                if nxt in VIET_STOPWORDS or len(nxt) < 2:
                    break
                result[j] = words[j][0].upper() + words[j][1:]
                j += 1
                count += 1
            i = j
        else:
            i += 1
    return ' '.join(result)

VN_NUM_MAP = {
    '0': chr(0x6b)+chr(0x68)+chr(0xf4)+chr(0x6e)+chr(0x67),
    '1': chr(0x6d)+chr(0x1ed9)+chr(0x74),
    '2': 'hai', '3': 'ba',
    '4': chr(0x62)+chr(0x1ed1)+chr(0x6e),
    '5': chr(0x6e)+chr(0x103)+chr(0x6d),
    '6': chr(0x73)+chr(0xe1)+chr(0x75),
    '7': chr(0x62)+chr(0x1ea3)+chr(0x79),
    '8': chr(0x74)+chr(0xe1)+chr(0x6d),
    '9': chr(0x63)+chr(0x68)+chr(0xed)+chr(0x6e),
    '10': chr(0x6d)+chr(0x1b0)+chr(0x1edd)+chr(0x69),
}
VN_WORD_MAP = {v: k for k, v in VN_NUM_MAP.items()}

def restore_year_context(text):
    """
    Phan biet '5' (so nam) vs 'nam' (year) bang ngu canh.
    Xu ly tat ca cach Speech API tach chu so:
      Dang A: "5 2, 0, 2, 6"  -> "nam 2026"  (dau phay sau tung chu so)
      Dang B: "5 2, 0, 18"    -> "nam 2018"  (2 chu so cuoi gop lai)
      Dang C: "5 2 0 2 5"     -> "nam 2025"  (chi khoang trang)
      Dang D: "5 2025"        -> "nam 2025"  (da gop san)
    """
    NAM = 'năm'
    SEP = r'[,\s]+'   # phan cach: phay va/hoac khoang trang

    # ƯU TIÊN CAO NHẤT: "2000 lẻ 5" / "5 2000 lẻ 5" -> "năm 2005"
    # Phai chay truoc cac rule gop chu so de tranh bi phan ra thanh tung phan
    def merge_le(m):
        base = int(m.group(1))
        tail = int(m.group(2))
        return NAM + ' ' + str(base + tail)
    text = re.sub(
        r'\b(?:5\s+|' + re.escape(NAM) + r'\s+)?((?:19|20)\d{2})\s+l[eẻ]\s+(\d{1,2})\b',
        merge_le, text, flags=re.IGNORECASE
    )

    # Dang A: 5 + 4 chu so don le, phan cach tuy y
    # "5 2, 0, 2, 6" -> "nam 2026"
    def join_4(m):
        year = m.group(1) + m.group(2) + m.group(3) + m.group(4)
        if year[:2] in ('19', '20'):
            return NAM + ' ' + year
        return m.group(0)
    text = re.sub(
        r'\b5\s+([12])' + SEP + r'([0-9])' + SEP + r'([0-9])' + SEP + r'([0-9])\b',
        join_4, text
    )

    # Dang B: 5 + 2 chu so don + 1 nhom 2 chu so
    # "5 2, 0, 18" -> "nam 2018"
    def join_3(m):
        year = m.group(1) + m.group(2) + m.group(3)
        if len(year) == 4 and year[:2] in ('19', '20'):
            return NAM + ' ' + year
        return m.group(0)
    text = re.sub(
        r'\b5\s+([12])' + SEP + r'([0-9])' + SEP + r'(\d{2})\b',
        join_3, text
    )

    # Dang D: "5 2025" (da la so 4 chu so hop le)
    text = re.sub(r'\b5\s+((?:19|20)\d{2})\b', NAM + r' \1', text)


    # Gop chu so roi khong co '5' phia truoc: "2, 0, 2, 5" -> "2025"
    def bare_4(m):
        year = m.group(1) + m.group(2) + m.group(3) + m.group(4)
        if year[:2] in ('19', '20'):
            return year
        return m.group(0)
    text = re.sub(
        r'\b([12])' + SEP + r'([0-9])' + SEP + r'([0-9])' + SEP + r'([0-9])\b',
        bare_4, text
    )

    # "tu chi year" tiep theo '5': hoc, nay, ngoai, truoc, sau, toi, qua...
    YEAR_AFTER = [
        'h\u1ecdc', 'nay', 'ngo\u00e1i', 'ngoai', 'tr\u01b0\u1edbc', 'truoc',
        't\u1edbi', 'toi', 'qua', 'sau', 'n\u1eefa', 'nua',
    ]
    for ya in YEAR_AFTER:
        text = re.sub(r'\b5\s+' + re.escape(ya) + r'\b',
                      NAM + ' ' + ya, text, flags=re.IGNORECASE)

    # "sinh vien 5" -> "sinh vien nam"
    SVN = r'(sinh\s+vi\u00ean|sinh\s+vien|h\u1ecdc\s+sinh|hoc\s+sinh|kh\u00f3a|khoa)\s+5\b'
    text = re.sub(SVN, lambda m: m.group(1) + ' ' + NAM, text, flags=re.IGNORECASE)
    return text



def normalize_viet_numbers(text):
    """Xoa trung lap, chuyen so truoc 'thu', phan biet year vs five."""
    for word, num in VN_WORD_MAP.items():
        text = re.sub(word + r'\s+' + num + r'(?=\s|$)', word, text, flags=re.IGNORECASE)
        text = re.sub(r'(?:^|\s)' + num + r'\s+' + word, ' ' + word, text, flags=re.IGNORECASE)
    thu = 'thứ'
    def to_word(m):
        return VN_NUM_MAP.get(m.group(1), m.group(1)) + ' ' + thu
    text = re.sub(r'(\d{1,2})\s+' + thu, to_word, text)
    text = restore_year_context(text)
    return text.strip()

def preprocess_for_translation(text, src_code):
    """Tien xu ly van ban truoc khi gui dich."""
    if src_code == 'vi':
        text = normalize_viet_numbers(text)
        text = capitalize_viet_names(text)
    return text

def translate_google(text, src_code, tgt_code):
    """Google Translate unofficial — khong can API key, nhanh nhat"""
    try:
        url = (
            "https://translate.googleapis.com/translate_a/single"
            f"?client=gtx&sl={src_code}&tl={tgt_code}&dt=t"
            f"&q={urllib.parse.quote(text)}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            translated = "".join(
                item[0] for item in data[0] if item and item[0]
            ).strip()
            if translated:
                return translated, "google-translate"
    except Exception as e:
        print(f"Google Translate error: {e}")
    return None, None


def translate_mymemory(text, src_code, tgt_code):
    """MyMemory API — backup khi Google loi"""
    try:
        lang_pair = f"{src_code}|{tgt_code}"
        url = (
            "https://api.mymemory.translated.net/get"
            f"?q={urllib.parse.quote(text)}&langpair={lang_pair}"
        )
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            translated = data.get("responseData", {}).get("translatedText", "")
            if translated and translated.lower() != text.lower():
                return translated, "mymemory"
    except Exception as e:
        print(f"MyMemory error: {e}")
    return None, None


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    from flask import make_response
    resp = make_response(send_from_directory(".", "index.html"))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    return resp



@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    text   = data.get("text", "").strip()
    source = data.get("source", "vi")
    target = data.get("target", "en")

    if not text:
        return jsonify({"translation": "", "engine": "none"})

    src_code = source.split("-")[0].lower()
    tgt_code = target.split("-")[0].lower()
    direction = f"{src_code}-{tgt_code}"

    # 0) Tien xu ly: viet hoa ten rieng Viet truoc khi dich
    print(f"[SERVER] Received: {text!r}")
    text = preprocess_for_translation(text, src_code)
    print(f"[SERVER] After preprocess: {text!r}")


    # 1) Google Translate (nhanh nhat, khong can key)
    result, engine = translate_google(text, src_code, tgt_code)
    if result:
        return jsonify({"translation": result, "engine": engine})

    # 2) MyMemory (backup)
    result, engine = translate_mymemory(text, src_code, tgt_code)
    if result:
        return jsonify({"translation": result, "engine": engine})

    # 3) Local dictionary — CUOI CUNG, chi khi mat mang hoan toan
    local_result = translate_phrase(text, direction)
    dictionary   = DICTIONARIES.get(direction, {})
    words        = text.lower().split()
    hit_count    = sum(1 for w in words if w.rstrip(".,!?;:") in dictionary)
    coverage     = round(hit_count / max(len(words), 1), 2)

    return jsonify({
        "translation": local_result or text,
        "engine": "local-offline",
        "coverage": coverage,
        "warning": "offline-partial" if coverage < 0.8 else "offline-ok"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "version": "2.0",
        "engines": ["local-dictionary", "online-mymemory-fallback"],
        "languages": list(set(k.split("-")[0] for k in DICTIONARIES.keys()))
    })


# ============================================================
# KHỞI ĐỘNG
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  [MIC] Voice Translator Server v2.0")
    print("  [OK]  Mo trinh duyet: http://localhost:5000")
    print("  [>>]  Engine: Dictionary local + MyMemory fallback")
    print("  [*]   Health: http://localhost:5000/health")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
