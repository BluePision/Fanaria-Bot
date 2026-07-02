from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "twitter.db"

class FanariaTwitterDB:
    def __init__(self, path: str | Path = DB_PATH):
        print(f"データベースを開きます: {path}")

        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self._create_tables()

        print("初期化が完了しました。")

    def _create_tables(self):
        print("テーブルを確認・作成します。")

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS fanaria_twitter_reactions (
                user_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                reaction TEXT NOT NULL,
                PRIMARY KEY (user_id, message_id, reaction)
            )
        """)

        self.conn.commit()

        print("テーブルの準備が完了しました。")

    def close(self):
        print("データベースを閉じます。")

        self.conn.close()

    def add_reaction(
        self,
        user_id: int,
        reaction: str,
        message_id: int
    ) -> None:
        """
        ユーザーが付けたリアクションをデータベースに登録します。

        既に同じユーザー・メッセージ・リアクションの組み合わせが登録されている場合は何もしません。

        Args:
            user_id (int): リアクションを付けたユーザーID
            reaction (str): リアクションの種類
            message_id (int): リアクションされたメッセージID
        """

        print(
            f"リアクションを追加します "
            f"(user_id={user_id}, reaction={reaction}, message_id={message_id})"
        )

        self.cursor.execute("""
            INSERT OR IGNORE INTO fanaria_twitter_reactions
            (user_id, message_id, reaction)
            VALUES (?, ?, ?)
        """, (user_id, message_id, reaction))

        self.conn.commit()

        if self.cursor.rowcount:
            print("リアクションを登録しました。")
        else:
            print("既に登録済みだったため追加しませんでした。")

    def remove_reaction(
        self,
        user_id: int,
        reaction: str,
        message_id: int
    ) -> None:
        """
        データベースからリアクション情報を削除します。

        Args:
            user_id (int): リアクションを外したユーザーID
            reaction (str): リアクションの種類
            message_id (int): リアクションされていたメッセージID
        """
        print(
            f"リアクションを削除します "
            f"(user_id={user_id}, reaction={reaction}, message_id={message_id})"
        )

        self.cursor.execute("""
            DELETE FROM fanaria_twitter_reactions
            WHERE user_id = ?
              AND message_id = ?
              AND reaction = ?
        """, (user_id, message_id, reaction))

        self.conn.commit()

        print(f"{self.cursor.rowcount}件削除しました。")

    def has_reaction(
        self,
        user_id: int,
        reaction: str,
        message_id: int
    ) -> bool:
        """
        指定したリアクション情報が既に登録されているか確認します。

        Args:
            user_id (int): ユーザーID
            reaction (str): リアクションの種類
            message_id (int): メッセージID

        Returns:
            bool:
                True なら登録済み、
                False なら未登録です。
        """
        print(
            f"リアクションの有無を確認します "
            f"(user_id={user_id}, reaction={reaction}, message_id={message_id})"
        )

        row = self.cursor.execute("""
            SELECT 1
            FROM fanaria_twitter_reactions
            WHERE user_id = ?
              AND message_id = ?
              AND reaction = ?
            LIMIT 1
        """, (user_id, message_id, reaction)).fetchone()

        result = row is not None

        print(f"確認結果: {'登録済み' if result else '未登録'}")

        return result

    def get_reactions(
        self,
        user_id: int,
        reaction: str
    ) -> list[int]:
        """
        指定したユーザーが付けたリアクションのメッセージID一覧を取得します。

        Args:
            user_id (int): ユーザーID
            reaction (str): リアクションの種類

        Returns:
            list[int]:
                指定したリアクションが付いているメッセージIDの一覧。
                登録が無い場合は空のリストを返します。
        """
        print(
            f"リアクション一覧を取得します "
            f"(user_id={user_id}, reaction={reaction})"
        )

        rows = self.cursor.execute("""
            SELECT message_id
            FROM fanaria_twitter_reactions
            WHERE user_id = ?
              AND reaction = ?
        """, (user_id, reaction)).fetchall()

        result = [row["message_id"] for row in rows]

        print(f"{len(result)}件取得しました。")

        return result

    def remove_message(self, message_id: int) -> None:
        """
        指定したメッセージIDに紐付く全てのリアクション情報を削除します。

        Args:
            message_id (int): 削除されたメッセージID
        """
        self.cursor.execute("""
            DELETE FROM fanaria_twitter_reactions
            WHERE message_id = ?
        """, (message_id,))

        self.conn.commit()

        print(f"{self.cursor.rowcount}件削除しました。")