from pathlib import Path
import sqlite3

class FanariaTwitterDB:
    def __init__(self, path: str = "fanaria/data/twitter.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS fanaria_twitter_reactions (
                user_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                reaction TEXT NOT NULL,
                PRIMARY KEY (user_id, message_id, reaction)
            )
        """)

        self.conn.commit()

    def close(self):
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
        self.cursor.execute("""
            INSERT OR IGNORE INTO fanaria_twitter_reactions
            (user_id, message_id, reaction)
            VALUES (?, ?, ?)
        """, (user_id, message_id, reaction))

        self.conn.commit()

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
        self.cursor.execute("""
            DELETE FROM fanaria_twitter_reactions
            WHERE user_id = ?
              AND message_id = ?
              AND reaction = ?
        """, (user_id, message_id, reaction))

        self.conn.commit()

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
        row = self.cursor.execute("""
            SELECT 1
            FROM fanaria_twitter_reactions
            WHERE user_id = ?
              AND message_id = ?
              AND reaction = ?
            LIMIT 1
        """, (user_id, message_id, reaction)).fetchone()

        return row is not None

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
        rows = self.cursor.execute("""
            SELECT message_id
            FROM fanaria_twitter_reactions
            WHERE user_id = ?
              AND reaction = ?
        """, (user_id, reaction)).fetchall()

        return [row["message_id"] for row in rows]

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