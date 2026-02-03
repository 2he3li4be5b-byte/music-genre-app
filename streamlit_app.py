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

# -----------------------------
# 質問と選択肢（10問）
# -----------------------------
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
    },
    "Q3. テンポの好みは？": {
        "ゆったり": {"LOFI": 3, "J-POP": 1},
        "普通": {"POP": 2, "J-POP": 2},
        "速い": {"EDM": 3, "ROCK": 2},
        "とにかく激しく": {"METAL": 3}
    },
    "Q4. ボーカルは重要？": {
        "とても重要": {"J-POP": 3, "POP": 2},
        "まあまあ": {"ROCK": 2, "HIPHOP": 2},
        "あまり重視しない": {"EDM": 3, "LOFI": 2}
    },
    "Q5. 歌詞の内容で惹かれるのは？": {
        "恋愛・感情": {"J-POP": 3, "POP": 2},
        "社会・メッセージ": {"HIPHOP": 3, "ROCK": 1},
        "雰囲気重視": {"LOFI": 3, "EDM": 2},
        "特に気にしない": {"EDM": 2, "METAL": 2}
    },
    "Q6. ライブに行くなら？": {
        "みんなで盛り上がりたい": {"ROCK": 3, "EDM": 2},
        "一体感のある会場": {"J-POP": 2, "POP": 2},
        "音に浸りたい": {"LOFI": 3},
        "激しい演奏を浴びたい": {"METAL": 3}
    },
    "Q7. よく聴く音量は？": {
        "小さめ": {"LOFI": 3, "POP": 1},
        "普通": {"J-POP": 2, "POP": 2},
        "大音量": {"ROCK": 3, "EDM": 2}
    },
    "Q8. 新しい音楽との出会い方は？": {
        "SNSやランキング": {"POP": 2, "J-POP": 2},
        "友人のおすすめ": {"ROCK": 2, "HIPHOP": 2},
        "作業用BGMから": {"LOFI": 3},
        "クラブ・イベント": {"EDM": 3}
    },
    "Q9. 英語詞と日本語詞、どっち派？": {
        "日本語詞": {"J-POP": 3},
        "英語詞": {"POP": 2, "EDM": 2},
        "どちらも好き": {"ROCK": 2, "HIPHOP": 2}
    },
    "Q10. 音楽に求める一番の役割は？": {
        "気分を上げる": {"EDM": 3, "POP": 2},
        "共感・感動": {"J-POP": 3},
        "集中力アップ": {"LOFI": 3},
        "ストレス発散": {"ROCK": 2, "METAL": 3}
    }
}

# -----------------------------
# ジャンル別おすすめアーティスト
# -----------------------------
artists = {
    "J-POP": ["米津玄師", "YOASOBI", "Official髭男dism"],
    "POP": ["Taylor Swift", "Ariana Grande", "Bruno Mars"],
    "HIPHOP": ["Kendrick Lamar", "Drake", "BAD HOP"],
    "ROCK": ["ONE OK ROCK", "Coldplay", "ASIAN KUNG-FU GENERATION"],
    "METAL": ["BABYMETAL", "Metallica", "Slipknot"],
    "EDM": ["Avicii", "Calvin Harris", "Martin Garrix"],
    "LOFI": ["Nujabes", "idealism", "Joji"]
}

# -----------------------------
# 全ジャンル抽出
# -----------------------------
all_genres = set()
for opts in questions.values():
    for gmap in opts.values():
        all_genres.update(gmap.keys())

# -----------------------------
# 質問表示
# -----------------------------
answers = {}
for q, options in questions.items():
    answers[q] = st.radio(q, list(options.keys()))

# -----------------------------
# 診断ボタン
# -----------------------------
if st.button("診断する"):
    scores = {g: 0 for g in all_genres}

    for q, answer in answers.items():
        for genre, point in questions[q][answer].items():
            scores[genre] += point

    best_genre = max(scores, key=scores.get)

    st.subheader("🎧 診断結果")
    st.write(f"あなたにおすすめの音楽ジャンルは **{best_genre}** です！")

    st.markdown("### 🎤 おすすめアーティスト")
    for artist in artists.get(best_genre, []):
        st.write(f"・{artist}")

    # -----------------------------
    # Supabase に保存
    # -----------------------------
    supabase.table("app_data").insert({
        "result": best_genre
    }).execute()

    st.success("診断結果を保存しました 🎉")

    st.subheader("📊 ジャンル別スコア")
    st.bar_chart(scores)
