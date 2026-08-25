"""파일 기반 영구 저장소 및 제너레이터 스트리밍 모듈"""

import json
from pathlib import Path
from typing import Generator, Optional, List
from budget_app.models import Transaction, Category, Budget


DEFAULT_CATEGORIES = ["food", "transport", "living", "shopping", "salary", "allowance", "etc"]


class CategoryStore:
    """카테고리 파일 저장소"""

    def __init__(self, data_dir: Path | str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.data_dir / "categories.jsonl"
        self._ensure_init()

    def _ensure_init(self) -> None:
        if not self.file_path.exists() or self.file_path.stat().st_size == 0:
            with open(self.file_path, "w", encoding="utf-8") as f:
                for cat in DEFAULT_CATEGORIES:
                    f.write(json.dumps({"name": cat}, ensure_ascii=False) + "\n")

    def get_all(self) -> list[str]:
        self._ensure_init()
        categories = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    categories.append(data.get("name", ""))
        return categories

    def exists(self, name: str) -> bool:
        return name.strip().lower() in [c.lower() for c in self.get_all()]

    def add(self, name: str) -> bool:
        name = name.strip()
        if not name or self.exists(name):
            return False
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"name": name}, ensure_ascii=False) + "\n")
        return True

    def remove(self, name: str) -> bool:
        name = name.strip()
        current = self.get_all()
        filtered = [c for c in current if c.lower() != name.lower()]
        if len(filtered) == len(current):
            return False
        with open(self.file_path, "w", encoding="utf-8") as f:
            for cat in filtered:
                f.write(json.dumps({"name": cat}, ensure_ascii=False) + "\n")
        return True


class BudgetStore:
    """예산 파일 저장소"""

    def __init__(self, data_dir: Path | str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.data_dir / "budgets.jsonl"

    def get_budget(self, month: str) -> Optional[Budget]:
        if not self.file_path.exists():
            return None
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    if data.get("month") == month:
                        return Budget.from_dict(data)
        return None

    def set_budget(self, budget: Budget) -> None:
        budgets = {}
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        budgets[data["month"]] = data
        budgets[budget.month] = budget.to_dict()

        with open(self.file_path, "w", encoding="utf-8") as f:
            for b in budgets.values():
                f.write(json.dumps(b, ensure_ascii=False) + "\n")


class TransactionRepository:
    """거래 내역 파일 저장소 (제너레이터 기반 스트리밍 처리)"""

    def __init__(self, data_dir: Path | str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.data_dir / "transactions.jsonl"

    def stream_all(self) -> Generator[Transaction, None, None]:
        """대용량 파일도 메모리 부담 없이 순회할 수 있는 스트리밍 제너레이터"""
        if not self.file_path.exists():
            return
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    yield Transaction.from_dict(data)

    def generate_next_id(self) -> str:
        """기존 거래 내역을 스트리밍하여 다음 TX-XXXXXX ID 생성"""
        max_num = 0
        for tx in self.stream_all():
            if tx.id.startswith("TX-"):
                try:
                    num = int(tx.id.replace("TX-", ""))
                    if num > max_num:
                        max_num = num
                except ValueError:
                    continue
        return f"TX-{(max_num + 1):06d}"

    def save(self, tx: Transaction) -> None:
        """신규 거래 저장 (Append)"""
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(tx.to_dict(), ensure_ascii=False) + "\n")

    def get_by_id(self, tx_id: str) -> Optional[Transaction]:
        """ID로 단일 거래 조회 (스트리밍)"""
        for tx in self.stream_all():
            if tx.id == tx_id:
                return tx
        return None

    def update(self, updated_tx: Transaction) -> bool:
        """기존 거래 수정"""
        found = False
        items: List[dict] = []
        for tx in self.stream_all():
            if tx.id == updated_tx.id:
                items.append(updated_tx.to_dict())
                found = True
            else:
                items.append(tx.to_dict())

        if not found:
            return False

        self._rewrite_all(items)
        return True

    def delete(self, tx_id: str) -> bool:
        """거래 삭제"""
        found = False
        items: List[dict] = []
        for tx in self.stream_all():
            if tx.id == tx_id:
                found = True
            else:
                items.append(tx.to_dict())

        if not found:
            return False

        self._rewrite_all(items)
        return True

    def _rewrite_all(self, items: List[dict]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
