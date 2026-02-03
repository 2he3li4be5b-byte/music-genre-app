import streamlit as st
from supabase import create_client

# -----------------------------
# Supabase 接続（最初に1回だけ）
# -----------------------------
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

st.set_page_config(page_title="音楽ジャンル診断", page_icon="🎵")

st.title("🎵 データで見る音楽ジャンル診断")
st.write("いくつかの質問に答えると、あなたに合った音楽ジャンルを診断します。")

# --- 質問と選択肢 ---
questions = {
    "Q1. 曲を聴くときに一番重視するのは？": {
        "メロディ": {"J-POP": 2, "POP": 2},
        "歌詞": {"J-POP": 3, "HIPHOP": 1},
        "リズム": {"HIPHOP": 3, "EDM": 2},
        "サウンドの迫力": {"ROCK": 3, "METAL": 2}
    },
    "Q2. 音楽をよく聴くシーンは？": {
        "勉強・作業中": {"POP": 2, "LOFI": 3},
        "通学・移動中": {"HIPHOP": 2, "ROCK": 2},
        "運動・トレーニング": {"EDM": 3, "ROCK": 2},
        "リラックスしたい時": {"J-POP": 2, "LOFI": 3}
    }
}

# --- ジャンル一覧 ---
all_genres = set()
for opts in questions.values():
    for gmap in opts.values():
        all_genres.update(gmap.keys())

# --- 質問表示 ---
answers = {}
for q, options in questions.items():
    answers[q] = st.radio(q, list(options.keys()))

# --- 診断ボタン ---
if st.button("診断する"):
    scores = {g: 0 for g in all_genres}

    for q, answer in answers.items():
        for genre, point in questions[q][answer].items():
            scores[genre] += point

    best_genre = max(scores, key=scores.get)

    st.subheader("🎧 診断結果")
    st.write(f"あなたにおすすめの音楽ジャンルは **{best_genre}** です！")

    # -----------------------------
    # Supabase に保存（重要）
    # -----------------------------
    supabase.table("app_data").insert({
        "result": best_genre
    }).execute()

    st.success("診断結果を保存しました 🎉")

    st.subheader("ジャンル別スコア")
    st.bar_chart(scores)
