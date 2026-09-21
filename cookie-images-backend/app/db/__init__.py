import json
import re
import dataset
from pathlib import Path
from sqlalchemy import event

from app.models.draw import DrawDocItem


_db = None


def get_db():
    global _db

    db_path = "sqlite:///" + str(Path(__file__).parent / "db.sqlite3")

    if _db is None:
        _db = dataset.connect(db_path)

        @event.listens_for(_db.engine, "connect")
        def _register_regexp(conn, _):
            conn.create_function(
                "REGEXP",
                2,
                lambda pat, val: bool(re.search(pat, val or "", re.IGNORECASE)),
            )

    return _db


def close_db():
    global _db
    _db = get_db().close()


class DrawTable:
    @staticmethod
    def _table():
        return get_db()["draw"]

    @staticmethod
    def table():
        return DrawTable._table()

    @staticmethod
    def _serialize(item: DrawDocItem) -> dict:
        data = item.model_dump(mode="json")
        if isinstance(data["pictures"], list):
            data["pictures"] = json.dumps(data["pictures"], ensure_ascii=False)
        return data

    @staticmethod
    def _deserialize(row) -> DrawDocItem:
        row = dict(row)
        pictures = row["pictures"]
        while isinstance(pictures, str):
            pictures = json.loads(pictures)
        row["pictures"] = pictures
        return DrawDocItem.model_validate(row)

    @classmethod
    def insert(cls, item: DrawDocItem):
        cls._table().insert(cls._serialize(item))

    @classmethod
    def insert_many(cls, items: list[DrawDocItem]):
        cls._table().upsert_many([cls._serialize(i) for i in items], ["dyn_id"])

    @classmethod
    def find(cls, **kwargs) -> list[DrawDocItem]:
        return [cls._deserialize(row) for row in cls._table().find(**kwargs)]

    @classmethod
    def find_one(cls, **kwargs) -> DrawDocItem | None:
        row = cls._table().find_one(**kwargs)
        return cls._deserialize(row) if row else None

    @classmethod
    def update(cls, item: DrawDocItem, keys: list[str]):
        cls._table().update(cls._serialize(item), keys)

    @classmethod
    def delete(cls, **kwargs):
        cls._table().delete(**kwargs)

    @classmethod
    def search(
        cls,
        pn: int = 0,
        ps: int = 20,
        order: str = "default",
        filter_type: list[str] | None = None,
        filter_user: list[int] | None = None,
        keyword: str = "",
    ) -> list[DrawDocItem]:
        conditions = []
        args = {}

        if keyword:
            conditions.append("(title REGEXP :keyword OR description REGEXP :keyword)")
            args["keyword"] = keyword

        if filter_user and filter_user != [-1]:
            for i, uid in enumerate(filter_user):
                args[f"uid_{i}"] = uid
            placeholders = ",".join(f":uid_{i}" for i in range(len(filter_user)))
            conditions.append(f"poster_uid IN ({placeholders})")

        if filter_type and "all" not in filter_type:
            type_conds = []
            for t in filter_type:
                if t == "pixiv":
                    type_conds.append("description REGEXP 'Pixiv ID'")
                elif t == "nico":
                    type_conds.append("description REGEXP 'im\\d+'")
                elif t == "x":
                    type_conds.append(
                        "description REGEXP '(twitter\\.com|x\\.com|t\\.co|\\d{12,})'"
                    )
            if type_conds:
                conditions.append(f"({' OR '.join(type_conds)})")

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        order_clause = {"random": "RANDOM()", "time_asc": "ctime ASC"}.get(
            order, "ctime DESC"
        )

        sql = f"SELECT * FROM draw {where} ORDER BY {order_clause} LIMIT {ps} OFFSET {(pn - 1) * ps}"
        return [cls._deserialize(row) for row in get_db().query(sql, **args)]
