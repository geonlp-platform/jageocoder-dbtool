from importlib.metadata import version
from typing import Generator, Optional


class CatalogException(Exception):
    pass


class Catalog(object):
    """
    データセットメタデータのコレクションの管理クラス
    """

    def __init__(self):
        self.catalog = {}

    def clear(self):
        self.catalog.clear()

    def add(self, meta: dict):
        if not self.validate_metadata(meta):
            raise CatalogException("メタデータの書式が正しくありません．")

        meta_id = meta["id"]
        if meta_id in self.catalog and \
                meta != self.catalog[meta_id]:
            raise CatalogException(
                f"同一のID({meta_id})で異なる内容のデータセットがあります")

        self.catalog[meta_id] = meta

    def get_records(self) -> Generator[dict, None, None]:
        """
        データベース登録用のメタデータリストを作成する
        """
        for id, meta in self.catalog.items():
            yield {
                "id": meta["id"],
                "title": meta["title"] if meta["title"] is not None else "",
                "url": meta["url"] if meta["url"] is not None else "",
            }

    @classmethod
    def get_version(cls):
        return version("jageocoder_dbtool")

    @classmethod
    def create_metadata(
        cls,
        id: int,
        title: str,
        url: Optional[str] = None,
    ) -> dict:
        id_val = int(id)
        if str(id_val) != str(id) or id_val < 1 or id_val >= 100:
            raise CatalogException("'id' は1から99の整数で指定してください")

        return {
            "jageocoder_meta": cls.get_version(),
            "id": id,
            "title": title[:512],
            "url": url if url is not None else "",
        }

    @classmethod
    def validate_metadata(cls, meta: dict) -> bool:
        if "jageocoder_meta" not in meta:
            return False

        if "id" not in meta:
            return False

        id_val = int(meta["id"])
        if id_val < 1 or id_val >= 100:
            return False

        if "title" not in meta:
            return False

        return True
