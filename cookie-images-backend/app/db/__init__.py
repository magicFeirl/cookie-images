import json
import dataset
from pathlib import Path

from app.models.draw import DrawDocItem


_db = None


def get_db():
    global _db

    db_path = "sqlite:///" + str(Path(__file__).parent / "db.sqlite3")

    if _db is None:
        _db = dataset.connect(db_path)

    return _db


def close_db():
    global _db
    _db = get_db().close()


class _DrawTable(dataset.Table):
    def __init__(self):
        super().__init__(get_db(), "draw", auto_create=True)

    def _serialize(self, item: DrawDocItem) -> dict:
        data = item.model_dump(mode="json")
        data["pictures"] = json.dumps(data["pictures"], ensure_ascii=False)
        return data

    def _deserialize(self, row) -> DrawDocItem:
        row = dict(row)
        row["pictures"] = json.loads(row["pictures"])
        return DrawDocItem.model_validate(row)

    def insert(self, item: DrawDocItem, **kwargs):
        return super().insert(self._serialize(item), **kwargs)

    def insert_many(self, items: list[DrawDocItem], **kwargs):
        return super().insert_many([self._serialize(i) for i in items], **kwargs)

    def find(self, **kwargs) -> list[DrawDocItem]:
        return [self._deserialize(row) for row in super().find(**kwargs)]

    def update(self, item: DrawDocItem, keys: list[str], **kwargs):
        return super().update(self._serialize(item), keys, **kwargs)

    def delete(self, **kwargs):
        return super().delete(**kwargs)


DrawTable = _DrawTable()
