import streamlit as st
import pandas as pd
import os
import random
import json
import re

# --- 設定 ---
st.set_page_config(page_title="CCNP Study App v12", layout="wide")
CSV_FILE = "ccnp_data.csv"
IMG_FOLDER = "ccnp_images"
HISTORY_FILE = "study_history.json"

# --- データロード関数 ---
@st.cache_data
def load_data():
    if not os.path.exists(CSV_FILE):
        return None
    try:
        df = pd.read_csv(CSV_FILE)
        df['id_num'] = df['id'].astype(str).str.extract(r'(\d+)').fillna(0).astype(int)
        df = df.sort_values('id_num').reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"データ読み込みエラー: {e}")
        return None

# --- 履歴管理 ---
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {"flagged": []}
    return {"flagged": []}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

# --- 初期化 ---
if 'history' not in st.session_state:
    st.session_state.history = load_history()
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False
if 'q_list' not in st.session_state:
    st.session_state.q_list = []
if 'shuffled_options' not in st.session_state:
    st.session_state.shuffled_options = None
if 'shuffled_for_id' not in st.session_state:
    st.session_state.shuffled_for_id = None

df = load_data()

# --- データチェック ---
if df is None:
    st.error(f"CSVファイル ({CSV_FILE}) が見つかりません。")
    st.stop()

# --- サイドバー：モード設定 ---
st.sidebar.title("Study Options")

mode_options = [
    "Sequential (順番通り)",
    "Range Selection (範囲指定)",
    "Range Selection (ランダム)",
    "Flagged Questions (フラグ付きのみ)",
    "Flagged Questions (ランダム)"
]

mode = st.sidebar.selectbox("Select Mode", mode_options)

start_q, end_q = 1, 100
if "Range Selection" in mode:
    max_q = int(df['id_num'].max()) if not df.empty else 1249
    c1, c2 = st.sidebar.columns(2)
    start_q = c1.number_input("From Q", 1, max_q, 1)
    end_q = c2.number_input("To Q", 1, max_q, min(100, max_q))

if st.sidebar.button("Start / Reset Session"):
    st.session_state.current_index = 0
    st.session_state.show_answer = False
    indices = []

    if mode == "Sequential (順番通り)":
        indices = df.index.tolist()
    elif "Range Selection" in mode:
        mask = (df['id_num'] >= start_q) & (df['id_num'] <= end_q)
        indices = df[mask].index.tolist()
        if "ランダム" in mode:
            random.shuffle(indices)
    elif "Flagged Questions" in mode:
        flagged_ids = st.session_state.history["flagged"]
        mask = df['id'].isin(flagged_ids)
        indices = df[mask].index.tolist()
        if "ランダム" in mode:
            random.shuffle(indices)

    st.session_state.q_list = indices
    st.rerun()

# --- メイン画面 ---
if not st.session_state.q_list:
    st.info("👈 サイドバーでモードを選択し、Startボタンを押してください。")
    if "Flagged" in mode:
        cnt = len(st.session_state.history["flagged"])
        st.warning(f"フラグ付きの問題数: {cnt}問")
    st.stop()

if st.session_state.current_index >= len(st.session_state.q_list):
    st.success("セッション終了！")
    if st.button("最初からやり直す"):
        st.session_state.current_index = 0
        st.rerun()
    st.stop()

try:
    current_row_idx = st.session_state.q_list[st.session_state.current_index]
    row = df.iloc[current_row_idx]
except IndexError:
    st.error("インデックスエラー。リセットしてください。")
    st.stop()

# UI表示
c1, c2, c3 = st.columns([6, 2, 2])
c1.title(f"{row['id']}")
c2.write(f"Count: {st.session_state.current_index + 1} / {len(st.session_state.q_list)}")

is_flagged = row['id'] in st.session_state.history["flagged"]
flag_label = "★ Flagged" if is_flagged else "☆ Flag"
if c3.button(flag_label):
    if is_flagged:
        st.session_state.history["flagged"].remove(row['id'])
    else:
        st.session_state.history["flagged"].append(row['id'])
    save_history(st.session_state.history)
    st.rerun()

st.progress((st.session_state.current_index + 1) / len(st.session_state.q_list))

st.markdown("### Question")
# 問題文の表示（Markdownを有効にして改行などを綺麗に見せる）
if pd.notna(row['question']):
    st.markdown(str(row['question']).replace('\n', '  \n'))
else:
    st.warning("Question text not available")

if pd.notna(row['images']) and str(row['images']).strip():
    img_files = [x.strip() for x in str(row['images']).split(',') if x.strip()]
    if img_files:
        if len(img_files) == 1:
            img_path = os.path.join(IMG_FOLDER, img_files[0])
            if os.path.exists(img_path):
                st.image(img_path)
        else:
            tabs = st.tabs([f"Exhibit {i+1}" for i in range(len(img_files))])
            for i, tab in enumerate(tabs):
                img_path = os.path.join(IMG_FOLDER, img_files[i])
                if os.path.exists(img_path):
                    with tab:
                        st.image(img_path)

# --- 選択肢表示ロジックの修正 ---
st.markdown("### Options")
options_str = str(row['options'])

if options_str and options_str.lower() != 'nan':
    lines = options_str.split('\n')
    formatted_options = []
    current_option = ""
    
    # "A.", "B." などのパターンで始まる行を検知
    option_pattern = re.compile(r"^[A-F]\.")
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        if option_pattern.match(line):
            if current_option:
                formatted_options.append(current_option)
            current_option = line
        else:
            # 続きの行は、Markdownの改行コードを入れて結合
            if current_option:
                current_option += "  \n&nbsp;&nbsp;&nbsp;&nbsp;" + line # インデントっぽく見せる
            else:
                current_option = line
    
    if current_option:
        formatted_options.append(current_option)
    
    # 問題が切り替わったときだけ順番をランダム化（回答の表示切替では順番維持）
    if st.session_state.shuffled_for_id != row['id'] or st.session_state.shuffled_options is None:
        shuffled = formatted_options.copy()
        # 元の順番（A, B, C...）には絶対にならないようにする
        for _ in range(10):
            random.shuffle(shuffled)
            if shuffled != formatted_options:
                break
        if shuffled == formatted_options and len(shuffled) > 1:
            shuffled[0], shuffled[1] = shuffled[1], shuffled[0]
        st.session_state.shuffled_options = shuffled
        st.session_state.shuffled_for_id = row['id']
    # 表示: st.infoだとボックスになるので、PDFっぽく見せるためにMarkdownを使用
    for opt in st.session_state.shuffled_options:
        # 背景色をつけたい場合は st.info でも良いが、ここでは読みやすさ優先でMarkdown
        st.info(opt) 
else:
    st.warning("選択肢なし")

st.divider()
if st.button("Show / Hide Answer"):
    st.session_state.show_answer = not st.session_state.show_answer

if st.session_state.show_answer:
    ans = row['answer'] if pd.notna(row['answer']) else "不明"
    st.success(f"**Correct Answer:** {ans}")

st.divider()
cp, cn = st.columns(2)
with cp:
    if st.button("⬅️ Previous"):
        if st.session_state.current_index > 0:
            st.session_state.current_index -= 1
            st.session_state.show_answer = False
            st.rerun()
with cn:
    if st.button("Next ➡️"):
        if st.session_state.current_index < len(st.session_state.q_list) - 1:
            st.session_state.current_index += 1
            st.session_state.show_answer = False
            st.rerun()
