"""비즈니스 로직 및 서비스 계층 모듈"""

import csv
from pathlib import Path
from typing import Optional, Any
from collections import defaultdict
from budget_app.models import (
    Transaction,
    Budget,
    ValidationError,
    validate_date,
    validate_month,
    validate_amount,
    validate_type,
)
from budget_app.storage import TransactionRepository, CategoryStore, BudgetStore


class BudgetService:
    """가계부 핵심 비즈니스 로직 서비스"""

    def __init__(self, data_dir: Path | str = "./data"):
        self.data_dir = Path(data_dir)
        self.repo = TransactionRepository(self.data_dir)
        self.cat_store = CategoryStore(self.data_dir)
        self.budget_store = BudgetStore(self.data_dir)

    def add_transaction(
        self,
        date: str,
        type_: str,
        category: str,
        amount: int | str,
        memo: str = "",
        tags: Optional[list[str]] = None,
    ) -> Transaction:
        """신규 거래 추가"""
        valid_date = validate_date(date)
        valid_type = validate_type(type_)
        valid_amount = validate_amount(amount)
        clean_category = (category or "").strip()

        if not self.cat_store.exists(clean_category):
            available = ", ".join(self.cat_store.get_all())
            raise ValidationError(
                f"등록되지 않은 카테고리입니다: '{clean_category}'",
                hint=f"사용 가능한 카테고리: {available} (카테고리 추가: category add)",
            )

        tx_id = self.repo.generate_next_id()
        tx = Transaction(
            id=tx_id,
            type=valid_type,
            date=valid_date,
            amount=valid_amount,
            category=clean_category,
            memo=memo.strip() if memo else "",
            tags=tags or [],
        )
        tx.validate()
        self.repo.save(tx)
        return tx

    def list_transactions(self, limit: Optional[int] = None) -> list[Transaction]:
        """최신순(date desc, id desc) 거래 목록 조회 (스트리밍 후 정렬)"""
        items = list(self.repo.stream_all())
        items.sort(key=lambda x: (x.date, x.id), reverse=True)
        if limit is not None and limit > 0:
            return items[:limit]
        return items

    def search_transactions(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        category: Optional[str] = None,
        type_: Optional[str] = None,
        query: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> list[Transaction]:
        """조건 기반 거래 검색 (최신순)"""
        if from_date:
            from_date = validate_date(from_date)
        if to_date:
            to_date = validate_date(to_date)
        if type_:
            type_ = validate_type(type_)

        results = []
        for tx in self.repo.stream_all():
            if from_date and tx.date < from_date:
                continue
            if to_date and tx.date > to_date:
                continue
            if category and tx.category.lower() != category.strip().lower():
                continue
            if type_ and tx.type != type_:
                continue
            if query:
                q = query.strip().lower()
                in_memo = q in tx.memo.lower()
                in_cat = q in tx.category.lower()
                in_id = q in tx.id.lower()
                in_tags = any(q in t.lower() for t in tx.tags)
                if not (in_memo or in_cat or in_id or in_tags):
                    continue
            if tag:
                t_search = tag.strip().lower()
                if not any(t_search == t.lower() for t in tx.tags):
                    continue
            results.append(tx)

        results.sort(key=lambda x: (x.date, x.id), reverse=True)
        return results

    def get_monthly_summary(self, month: str, top_n: int = 3) -> dict[str, Any]:
        """월별 요약 리포트 생성"""
        valid_month = validate_month(month)
        matching_txs = [tx for tx in self.repo.stream_all() if tx.date.startswith(valid_month)]

        if not matching_txs:
            return {
                "has_data": False,
                "month": valid_month,
                "total_income": 0,
                "total_expense": 0,
                "balance": 0,
                "top_expenses": [],
                "budget_amount": None,
                "usage_rate": None,
                "is_over_budget": False,
            }

        total_income = sum(tx.amount for tx in matching_txs if tx.type == "income")
        total_expense = sum(tx.amount for tx in matching_txs if tx.type == "expense")
        balance = total_income - total_expense

        category_expenses: dict[str, int] = defaultdict(int)
        for tx in matching_txs:
            if tx.type == "expense":
                category_expenses[tx.category] += tx.amount

        sorted_categories = sorted(category_expenses.items(), key=lambda x: x[1], reverse=True)
        top_expenses = sorted_categories[:top_n]

        budget = self.budget_store.get_budget(valid_month)
        budget_amount = budget.amount if budget else None
        usage_rate = None
        is_over_budget = False

        if budget_amount is not None:
            if budget_amount > 0:
                usage_rate = round((total_expense / budget_amount) * 100, 1)
            else:
                usage_rate = 0.0 if total_expense == 0 else 100.0
            is_over_budget = total_expense > budget_amount

        return {
            "has_data": True,
            "month": valid_month,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "top_expenses": top_expenses,
            "budget_amount": budget_amount,
            "usage_rate": usage_rate,
            "is_over_budget": is_over_budget,
        }

    def set_budget(self, month: str, amount: int | str) -> Budget:
        """월별 예산 설정"""
        valid_month = validate_month(month)
        valid_amount = validate_amount(amount)
        budget = Budget(month=valid_month, amount=valid_amount)
        budget.validate()
        self.budget_store.set_budget(budget)
        return budget

    def category_add(self, name: str) -> bool:
        """카테고리 추가"""
        clean = (name or "").strip()
        if not clean:
            raise ValidationError("카테고리명은 비어있을 수 없습니다.", hint="예: food, travel")
        if self.cat_store.exists(clean):
            raise ValidationError(f"이미 존재하는 카테고리입니다: '{clean}'")
        return self.cat_store.add(clean)

    def category_list(self) -> list[str]:
        """카테고리 목록 조회"""
        return self.cat_store.get_all()

    def category_remove(self, name: str, replacement: Optional[str] = None) -> None:
        """카테고리 삭제 (사용 중인 경우 대체 카테고리 필요)"""
        clean = (name or "").strip()
        if not self.cat_store.exists(clean):
            raise ValidationError(f"존재하지 않는 카테고리입니다: '{clean}'")

        # 사용 중인지 확인
        in_use_txs = [tx for tx in self.repo.stream_all() if tx.category.lower() == clean.lower()]
        if in_use_txs:
            if not replacement:
                raise ValidationError(
                    f"카테고리 '{clean}'은(는) {len(in_use_txs)}건의 거래 내역에서 사용 중입니다.",
                    hint="대체할 카테고리를 지정하거나(--replace <대체카테고리>), 해당 거래 내역을 먼저 삭제/수정하세요.",
                )
            clean_rep = replacement.strip()
            if clean_rep.lower() == clean.lower() or not self.cat_store.exists(clean_rep):
                raise ValidationError(
                    f"대체 카테고리가 유효하지 않거나 등록되지 않았습니다: '{clean_rep}'",
                    hint=f"등록된 카테고리 목록: {', '.join(self.cat_store.get_all())}",
                )
            # 거래 내역의 카테고리 일괄 변경
            for tx in in_use_txs:
                tx.category = clean_rep
                self.repo.update(tx)

        self.cat_store.remove(clean)

    def update_transaction(
        self,
        tx_id: str,
        date: Optional[str] = None,
        type_: Optional[str] = None,
        category: Optional[str] = None,
        amount: Optional[int | str] = None,
        memo: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> Transaction:
        """거래 수정"""
        tx = self.repo.get_by_id(tx_id)
        if not tx:
            raise ValidationError(
                f"거래 ID '{tx_id}'를 찾을 수 없습니다.",
                hint="거래 목록(list)에서 정확한 ID를 확인하세요.",
            )

        if date is not None:
            tx.date = validate_date(date)
        if type_ is not None:
            tx.type = validate_type(type_)
        if category is not None:
            cat_clean = category.strip()
            if not self.cat_store.exists(cat_clean):
                raise ValidationError(
                    f"등록되지 않은 카테고리입니다: '{cat_clean}'",
                    hint=f"사용 가능한 카테고리: {', '.join(self.cat_store.get_all())}",
                )
            tx.category = cat_clean
        if amount is not None:
            tx.amount = validate_amount(amount)
        if memo is not None:
            tx.memo = memo.strip()
        if tags is not None:
            tx.tags = tags

        tx.validate()
        self.repo.update(tx)
        return tx

    def delete_transaction(self, tx_id: str) -> bool:
        """거래 삭제"""
        if not self.repo.delete(tx_id):
            raise ValidationError(
                f"거래 ID '{tx_id}'를 찾을 수 없습니다.",
                hint="삭제할 거래 ID를 다시 확인하세요.",
            )
        return True

    def export_to_csv(
        self,
        filepath: Path | str,
        month: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> int:
        """거래 내역 CSV 내보내기"""
        if not month and not (from_date and to_date):
            raise ValidationError(
                "내보내기 조건으로 --month 또는 (--from 및 --to)가 필요합니다.",
                hint="예: export --out data.csv --month 2024-01",
            )

        if month:
            from_date = f"{validate_month(month)}-01"
            to_date = f"{validate_month(month)}-31"
        else:
            from_date = validate_date(from_date)  # type: ignore
            to_date = validate_date(to_date)  # type: ignore

        records = self.search_transactions(from_date=from_date, to_date=to_date)
        # 내보내기 시 오래된 날짜 -> 최신순 또는 최신순(정렬)
        records.sort(key=lambda x: (x.date, x.id))

        out_path = Path(filepath)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "type", "category", "amount", "memo", "tags"])
            for r in records:
                writer.writerow([r.date, r.type, r.category, r.amount, r.memo, ",".join(r.tags)])

        return len(records)

    def import_from_csv(self, filepath: Path | str) -> tuple[int, int]:
        """CSV 파일에서 거래 내역 일괄 등록"""
        in_path = Path(filepath)
        if not in_path.exists():
            raise ValidationError(
                f"가져올 CSV 파일을 찾을 수 없습니다: {filepath}",
                hint="파일 경로를 확인하세요.",
            )

        imported = 0
        skipped = 0

        with open(in_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValidationError("CSV 파일이 비어있거나 올바른 형식이 아닙니다.")

            required_cols = {"date", "type", "category", "amount"}
            if not required_cols.issubset(set(reader.fieldnames)):
                raise ValidationError(
                    f"CSV 헤더에 필수 컬럼이 누락되었습니다: {required_cols - set(reader.fieldnames)}",
                    hint="필수 헤더: date, type, category, amount, memo, tags",
                )

            for row in reader:
                try:
                    cat = (row.get("category") or "").strip()
                    if not self.cat_store.exists(cat):
                        self.cat_store.add(cat)

                    tags_str = row.get("tags", "") or ""
                    tags = [t.strip() for t in tags_str.split(",") if t.strip()]

                    self.add_transaction(
                        date=row.get("date", ""),
                        type_=row.get("type", ""),
                        category=cat,
                        amount=row.get("amount", 0),
                        memo=row.get("memo", "") or "",
                        tags=tags,
                    )
                    imported += 1
                except Exception:
                    skipped += 1

        return imported, skipped
