import streamlit as st
import sqlite3
from pathlib import Path
from contextlib import closing

# -----------------------------
# SQLite3 データベース設定
# -----------------------------
# データベースファイルは、このスクリプトと同じフォルダに作成する
DB_PATH = Path(__file__).resolve().parent / "music_genre.db"


def get_connection():
    """SQLite3への接続を作成する。"""
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """データベースとテーブルが存在しない場合は作成する。"""
    with closing(get_connection()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS app_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def insert_result(result):
    """診断結果を登録する。SQLの値にはプレースホルダーを使う。"""
    with closing(get_connection()) as conn:
        cursor = conn.execute(
            "INSERT INTO app_data (result) VALUES (?)",
            (result,)
        )
        conn.commit()
        return cursor.lastrowid


def get_results():
    """保存済みの診断結果を新しい順に取得する。"""
    with closing(get_connection()) as conn:
        rows = conn.execute("""
            SELECT id, result, created_at
            FROM app_data
            ORDER BY id DESC
        """).fetchall()
        return [dict(row) for row in rows]


def update_result(record_id, new_result):
    """指定したIDの診断結果を更新する。"""
    with closing(get_connection()) as conn:
        cursor = conn.execute(
            "UPDATE app_data SET result = ? WHERE id = ?",
            (new_result, record_id)
        )
        conn.commit()
        return cursor.rowcount > 0


def delete_result(record_id):
    """指定したIDの診断結果を削除する。"""
    with closing(get_connection()) as conn:
        cursor = conn.execute(
            "DELETE FROM app_data WHERE id = ?",
            (record_id,)
        )
        conn.commit()
        return cursor.rowcount > 0


# アプリ起動時にデータベースとテーブルを初期化
init_database()

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
    # SQLite3 に保存
    # -----------------------------
    try:
        insert_result(best_genre)
        st.success("診断結果を保存しました 🎉")
    except sqlite3.Error as e:
        st.error(f"診断結果の保存に失敗しました: {e}")

    st.subheader("📊 ジャンル別スコア")
    st.bar_chart(scores)
