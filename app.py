"""Math Quest v0.6 (Streamlit edition) — original Gradio learning logic preserved."""
import streamlit as st

import random
import html
import copy

# 각 단계는 고정된 학습 개념을 가집니다. 최대 6단계이며 마지막 단계는 반복합니다.
LEVELS = [
    ("5 이하 덧셈", "두 수의 합이 5 이하"),
    ("10 이하 덧셈", "두 수의 합이 10 이하"),
    ("10 만들기", "합이 정확히 10"),
    ("받아올림 연습", "한 자리 수 + 한 자리 수, 합이 11~18"),
    ("20 이하 혼합 덧셈", "합이 20 이하인 덧셈"),
    ("두 자리 수 덧셈", "두 자리 수 + 한 자리 수, 합이 99 이하"),
]
QUESTIONS_PER_ROUND = 5
PASS_SCORE = 4


def make_question(level, avoid=None):
    """단계 학습 목표를 만족하는 덧셈 한 문제 생성."""
    level = min(max(int(level), 1), len(LEVELS))
    avoid = avoid or []
    candidates = []
    if level == 1:
        candidates = [(a, b) for a in range(1, 5) for b in range(a, 5) if a+b <= 5]
    elif level == 2:
        candidates = [(a, b) for a in range(1, 10) for b in range(a, 10) if a+b <= 10]
    elif level == 3:
        candidates = [(a, 10-a) for a in range(1, 6)]
    elif level == 4:
        candidates = [(a, b) for a in range(2, 10) for b in range(a, 10) if 11 <= a+b <= 18]
    elif level == 5:
        candidates = [(a, b) for a in range(1, 20) for b in range(a, 20) if a+b <= 20]
    else:
        candidates = [(a, b) for a in range(10, 90) for b in range(1, 10) if a+b <= 99]
    fresh = [q for q in candidates if q not in avoid]
    return random.choice(fresh or candidates)


def initial_state():
    return {
        "level": 1, "score": 0, "count": 0, "correct": 0,
        "question": make_question(1), "mode": "normal",
        "wrong": [], "review_index": 0, "review_correct": 0,
        "recent": [], "level_attempts": {},
        "badges": [], "streak": 0, "best_streak": 0, "normal_total": 0,
    }


def add_wrong(state, a, b):
    a, b = sorted((int(a), int(b)))
    for item in state["wrong"]:
        if (item["a"], item["b"]) == (a, b):
            item["times"] += 1
            return
    state["wrong"].append({"a": a, "b": b, "times": 1})


def show_wrong(state):
    if not state["wrong"]:
        return "### 📒 오답노트\n복습할 오답이 없습니다. 🎉"
    lines = ["### 📒 오답노트", "복습에서 맞히면 목록에서 제거됩니다."]
    for i, item in enumerate(state["wrong"], 1):
        lines.append(f"{i}. **{item['a']} + {item['b']} = {item['a']+item['b']}** (오답 {item['times']}회)")
    return "\n\n".join(lines)


def show_game(state):
    a, b = state["question"]
    level = min(state["level"], len(LEVELS))
    name, description = LEVELS[level-1]
    review = state["mode"] == "review"
    progress = 0 if review else state["count"] / QUESTIONS_PER_ROUND * 100
    status = f"오답 복습: {len(state['wrong'])}문제 남음" if review else f"진행도 {state['count']}/{QUESTIONS_PER_ROUND}"
    return f"""
    <div style="background:linear-gradient(135deg,#e5f8ed,#dceaff);border-radius:22px;padding:28px;text-align:center;color:#213349">
      <h1>{'📘 오답 복습 훈련소' if review else '🏰 Math Quest'}</h1>
      <h2>⭐ 레벨 {level} — {html.escape(name)}</h2>
      <p>{html.escape(description)}</p>
      <div style="font-size:52px">{'📖 🧠 ✏️' if review else '🧙‍♂️ 🗝️ 🏰'}</div>
      <div style="background:#cdd6e3;border-radius:10px;height:14px;overflow:hidden">
        <div style="background:#28a978;height:100%;width:{progress:.0f}%"></div>
      </div>
      <p>{status}</p><h1>{a} + {b} = ?</h1>
      <h3>🏆 점수 {state['score']} | 📒 남은 오답 {len(state['wrong'])}</h3>
    </div>"""


def next_normal_question(state):
    state["question"] = make_question(state["level"], state.get("recent", []))
    state["recent"] = (state.get("recent", []) + [state["question"]])[-4:]


def check(answer, state):
    state = copy.deepcopy(state)
    if answer is None or answer == "":
        return show_game(state), "⚠️ 정답을 입력해 주세요.", show_wrong(state), state
    try:
        value = float(answer)
        if not value.is_integer():
            raise ValueError
    except (ValueError, TypeError):
        return show_game(state), "⚠️ 정수를 입력해 주세요.", show_wrong(state), state
    a, b = state["question"]
    correct = int(value) == a+b
    if state["mode"] == "review":
        idx = state["review_index"]
        if correct:
            state["wrong"].pop(idx)
            state["review_correct"] += 1
            state["score"] += 10
            msg = "✅ 복습 성공! 오답노트에서 제거했어요."
        else:
            item = state["wrong"].pop(idx)
            item["times"] += 1
            state["wrong"].append(item)
            msg = f"📚 정답은 {a+b}. 다시 도전해 보세요."
        if not state["wrong"]:
            state["mode"] = "normal"
            state["review_index"] = 0
            next_normal_question(state)
            msg += " 🎉 복습 완료!"
        else:
            state["review_index"] = idx % len(state["wrong"])
            item = state["wrong"][state["review_index"]]
            state["question"] = (item["a"], item["b"])
    else:
        state["count"] += 1
        state["normal_total"] += 1
        if correct:
            state["correct"] += 1
            state["score"] += 10
            state["streak"] += 1
            state["best_streak"] = max(state["best_streak"], state["streak"])
            msg = "🎉 정답입니다!"
        else:
            add_wrong(state, a, b)
            state["streak"] = 0
            msg = f"📚 정답은 {a+b}. 오답노트에 저장했습니다."
        if state["count"] == QUESTIONS_PER_ROUND:
            lvl = state["level"]
            state["level_attempts"].setdefault(str(lvl), []).append(state["correct"])
            if state["correct"] >= PASS_SCORE:
                if lvl < len(LEVELS):
                    state["level"] += 1
                    msg += " 🏆 다음 레벨을 열었습니다!"
                else:
                    msg += " 🏅 모든 레벨 통과! 최고 레벨을 계속 연습합니다."
            else:
                msg += " 🔄 현재 레벨에서 다시 도전합니다."
            state["count"], state["correct"] = 0, 0
        next_normal_question(state)
    earned = grant_badges(state)
    if earned:
        msg += " 🎖️ 새 배지: " + ", ".join(earned)
    return show_game(state), msg, show_wrong(state), state


def start_review(state):
    state = copy.deepcopy(state)
    if not state["wrong"]:
        return show_game(state), "📒 복습할 문제가 없습니다.", show_wrong(state), state
    state["mode"] = "review"
    state["review_index"] = 0
    item = state["wrong"][0]
    state["question"] = (item["a"], item["b"])
    return show_game(state), "📘 오답 복습을 시작합니다.", show_wrong(state), state


def go_normal(state):
    state = copy.deepcopy(state)
    state["mode"] = "normal"
    next_normal_question(state)
    return show_game(state), "🏰 일반 학습으로 돌아왔습니다.", show_wrong(state), state

BADGE_RULES = {
    "🌱 첫걸음": "첫 문제를 맞혔어요",
    "🔥 연속 정답": "연속 5문제를 맞혔어요",
    "📘 오답 정복자": "오답 5문제를 복습하여 해결했어요",
    "🏅 덧셈 마스터": "최종 레벨을 통과했어요",
}


def grant_badges(state):
    earned = []
    checks = [
        ("🌱 첫걸음", state["score"] >= 10),
        ("🔥 연속 정답", state["best_streak"] >= 5),
        ("📘 오답 정복자", state["review_correct"] >= 5),
        ("🏅 덧셈 마스터", any(n >= PASS_SCORE for n in state["level_attempts"].get(str(len(LEVELS)), []))),
    ]
    for badge, yes in checks:
        if yes and badge not in state["badges"]:
            state["badges"].append(badge)
            earned.append(badge)
    return earned


def show_badges(state):
    items = []
    for badge, desc in BADGE_RULES.items():
        unlocked = badge in state["badges"]
        items.append(f"<div style='background:{'#e4f9ec' if unlocked else '#f0f1f4'};padding:14px;border-radius:14px;min-width:150px;flex:1'>"
                     f"<b>{badge if unlocked else '🔒 '+html.escape(badge.split(' ',1)[1])}</b><br>"
                     f"<small>{html.escape(desc)}</small></div>")
    return "<div style='display:flex;flex-wrap:wrap;gap:9px;color:#203047'>" + "".join(items) + "</div>"

WORLD_NAMES = ["숫자 숲", "덧셈 마을", "10의 탑", "받아올림 성", "모험 동굴", "수학 왕궁"]
WORLD_ICONS = ["🌲", "🏘️", "🗼", "🏰", "🪨", "👑"]


def show_map(state):
    current = state["level"]
    cards = []
    for idx, (name, icon) in enumerate(zip(WORLD_NAMES, WORLD_ICONS), 1):
        status = "✅ 완료" if idx < current else ("▶️ 도전 중" if idx == current else "🔒 잠김")
        bg = "#d6f4e1" if idx < current else ("#ffedbd" if idx == current else "#edf0f4")
        cards.append(f"<div style='background:{bg};padding:17px;border-radius:18px;min-width:130px;flex:1;text-align:center'>"
                     f"<div style='font-size:37px'>{icon}</div><b>{idx}. {html.escape(name)}</b>"
                     f"<div style='font-size:13px'>{status}</div></div>")
    return "<div style='display:flex;flex-wrap:wrap;gap:10px;color:#26364b'>"+"".join(cards)+"</div>"

import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone


def show_stats(state):
    attempts = state.get("level_attempts", {})
    cards = [f"<div style='padding:12px;border-radius:12px;background:#eef7ff;flex:1'>"
             f"<b>레벨 {level}</b><br>최근 결과: {values[-1]}/5점<br>도전 {len(values)}회</div>"
             for level, values in sorted(attempts.items(), key=lambda e: int(e[0])) if values]
    if not cards:
        return "<p>아직 완료된 5문제 묶음이 없습니다. 문제를 풀면 여기에 기록됩니다.</p>"
    return "<div style='display:flex;flex-wrap:wrap;gap:10px;color:#26364b'>"+"".join(cards)+"</div>"


def validate_record(data):
    if not isinstance(data, dict):
        raise ValueError("학습 기록 형식이 올바르지 않습니다.")
    if data.get("app") != "mathquest" or data.get("schema") != 1:
        raise ValueError("Math Quest 저장 파일이 아닙니다.")
    s = data.get("state")
    if not isinstance(s, dict):
        raise ValueError("학습 상태가 없습니다.")
    needed = ("level", "score", "count", "correct", "question", "wrong", "mode")
    if any(k not in s for k in needed):
        raise ValueError("필수 학습 기록이 누락되었습니다.")
    if not isinstance(s["level"], int) or not 1 <= s["level"] <= len(LEVELS):
        raise ValueError("잘못된 레벨입니다.")
    if s["mode"] not in ("normal", "review"):
        raise ValueError("잘못된 학습 모드입니다.")
    if not isinstance(s["question"], list) or len(s["question"]) != 2:
        raise ValueError("문제 형식이 올바르지 않습니다.")
    if not isinstance(s["wrong"], list) or len(s["wrong"]) > 5000:
        raise ValueError("오답 기록이 올바르지 않습니다.")
    for item in s["wrong"]:
        if not isinstance(item, dict) or not all(isinstance(item.get(k), int) for k in ("a", "b", "times")):
            raise ValueError("오답 항목이 올바르지 않습니다.")
    normalized = initial_state()
    normalized.update({k: v for k, v in s.items() if k in normalized})
    normalized["question"] = tuple(normalized["question"])
    normalized["recent"] = [tuple(q) for q in normalized.get("recent", [])]
    if normalized["mode"] == "review":
        if not normalized["wrong"]:
            normalized["mode"] = "normal"
            next_normal_question(normalized)
        else:
            normalized["review_index"] = min(max(0, int(normalized["review_index"])), len(normalized["wrong"])-1)
            item = normalized["wrong"][normalized["review_index"]]
            normalized["question"] = (item["a"], item["b"])
    return normalized


def export_record(state):
    content = {"app": "mathquest", "schema": 1, "saved_at": datetime.now(timezone.utc).isoformat(), "state": state}
    path = Path(tempfile.mkdtemp(prefix="mathquest_")) / "mathquest_record.json"
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path), "✅ 저장 파일을 다운로드하여 보관하세요."


def import_record(file, state):
    if file is None:
        return (show_game(state), "⚠️ 복원할 JSON 파일을 선택하세요.", show_wrong(state),
                show_badges(state), show_map(state), show_stats(state), state)
    try:
        path = file if isinstance(file, str) else file.name
        if Path(path).stat().st_size > 2_000_000:
            raise ValueError("저장 파일이 너무 큽니다.")
        saved = json.loads(Path(path).read_text(encoding="utf-8"))
        loaded = validate_record(saved)
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return (show_game(state), f"⚠️ 불러오기 실패: {html.escape(str(exc))}", show_wrong(state),
                show_badges(state), show_map(state), show_stats(state), state)
    return (show_game(loaded), "✅ 저장한 학습 기록을 복원했습니다.", show_wrong(loaded),
            show_badges(loaded), show_map(loaded), show_stats(loaded), loaded)


def screen_check(answer, state):
    game, msg, wrong, st = check(answer, state)
    return (game, msg, wrong, show_badges(st), show_map(st), show_stats(st), st)

def screen_review(state):
    game, msg, wrong, st = start_review(state)
    return (game, msg, wrong, show_badges(st), show_map(st), show_stats(st), st)

def screen_normal(state):
    game, msg, wrong, st = go_normal(state)
    return (game, msg, wrong, show_badges(st), show_map(st), show_stats(st), st)



st.set_page_config(page_title="Math Quest v0.6", page_icon="🎮", layout="wide")
st.markdown("""<style>
.block-container{max-width:1050px;padding-top:1.6rem}
.stButton button {border-radius:12px}
[data-testid="stMetric"] {background:#f1f6ff;padding:13px;border-radius:14px}
</style>""", unsafe_allow_html=True)

if "mathquest_state" not in st.session_state:
    st.session_state.mathquest_state = initial_state()
if "mathquest_notice" not in st.session_state:
    st.session_state.mathquest_notice = "문제를 풀어 보세요!"

state = st.session_state.mathquest_state
st.title("🎮 Math Quest v0.6")
st.caption("단계별 덧셈 · 오답 복습 · 배지 · 모험 지도 · 학습 기록 저장")

with st.sidebar:
    st.header("🧭 학습 메뉴")
    st.metric("현재 레벨", f"{state['level']} / {len(LEVELS)}")
    st.metric("누적 점수", state['score'])
    st.metric("복습할 문제", len(state['wrong']))
    if st.button("📒 오답 복습 시작", use_container_width=True):
        _, msg, _, state = start_review(state)
        st.session_state.mathquest_state = state
        st.session_state.mathquest_notice = msg
        st.rerun()
    if st.button("🏰 일반 학습으로", use_container_width=True):
        _, msg, _, state = go_normal(state)
        st.session_state.mathquest_state = state
        st.session_state.mathquest_notice = msg
        st.rerun()
    st.divider()
    st.caption("저장하기를 누르면 JSON 파일을 내려받을 수 있습니다. 학습 기록은 서버에 자동 보관되지 않습니다.")

st.markdown(show_game(state), unsafe_allow_html=True)
st.info(st.session_state.mathquest_notice)

with st.form("answer_form", clear_on_submit=True):
    answer = st.number_input("정답 입력", min_value=0, max_value=9999, step=1, value=None, placeholder="정답을 입력하세요")
    submitted = st.form_submit_button("⚔️ 정답 확인", type="primary", use_container_width=True)
if submitted:
    _, msg, _, state = check(answer, st.session_state.mathquest_state)
    st.session_state.mathquest_state = state
    st.session_state.mathquest_notice = msg
    st.rerun()

st.divider()
tab_wrong, tab_badge, tab_map, tab_stats, tab_save = st.tabs([
    "📒 오답노트", "🏅 배지", "🗺️ 모험 지도", "📊 학습 통계", "💾 기록 저장·복원"
])
with tab_wrong:
    st.markdown(show_wrong(state))
with tab_badge:
    st.markdown(show_badges(state), unsafe_allow_html=True)
with tab_map:
    st.markdown(show_map(state), unsafe_allow_html=True)
with tab_stats:
    st.markdown(show_stats(state), unsafe_allow_html=True)
    attempts=state.get("level_attempts", {})
    if attempts:
        chart_data={f"레벨 {i}": sum(vals)/len(vals) for i in range(1,len(LEVELS)+1)
                    if (vals:=attempts.get(str(i),[]))}
        if chart_data:
            st.subheader("단계별 평균 정답 수 (5문제 기준)")
            st.bar_chart(chart_data, horizontal=True, x_label="정답 개수", y_label="학습 단계")
with tab_save:
    st.subheader("💾 학습 기록 보관")
    st.write("기록 저장은 JSON 다운로드 방식입니다. 이전 Gradio v06의 JSON 파일도 불러올 수 있습니다.")
    record = {
        "app":"mathquest", "schema":1,
        "saved_at":datetime.now(timezone.utc).isoformat(),
        "state":state,
    }
    st.download_button(
        "⬇️ 현재 학습 기록 다운로드",
        data=json.dumps(record, ensure_ascii=False, indent=2),
        file_name="mathquest_record.json", mime="application/json", use_container_width=True
    )
    uploaded=st.file_uploader("기존 학습 기록 (.json) 선택", type=["json"])
    if st.button("📂 선택한 학습 기록 불러오기", disabled=uploaded is None, use_container_width=True):
        try:
            if uploaded.size>2_000_000:
                raise ValueError("저장 파일이 너무 큽니다.")
            loaded=validate_record(json.loads(uploaded.getvalue().decode("utf-8")))
            st.session_state.mathquest_state=loaded
            st.session_state.mathquest_notice="✅ 저장한 학습 기록을 복원했습니다."
            st.rerun()
        except (ValueError, UnicodeDecodeError, TypeError, KeyError, IndexError) as exc:
            st.error(f"불러오기 실패: {exc}")
    st.caption("주의: Streamlit Community Cloud에서는 서버 파일에 저장한 학습 기록이 유지된다고 보장할 수 없습니다. JSON 파일을 내려받아 보관하세요.")
