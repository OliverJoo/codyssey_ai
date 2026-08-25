"""보너스 과제 구현 모듈 (기본 클래스 상속 및 기능 확장)

1. 백업 기능 (Backup)
2. 반복 내역 기능 (Recurring Transactions)
3. 테이블 출력 포맷터 (Table Formatter without external libraries)
4. 저장 원자성 강화 (Atomic Storage with tempfile and os.replace)
"""

import os
import json
import shutil
import tempfile
import zipfile
import unicodedata
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Any, List, Sequence
import argparse
import sys

from budget_app.models import (
    Transaction,
    ValidationError,
    validate_month,
    validate_amount,
    validate_type,
)
from budget_app.storage import TransactionRepository
from budget_app.service import BudgetService
from budget_app.cli import BudgetCLI, build_parser
from budget_app.decorators import handle_cli_errors


class AtomicTransactionRepository(TransactionRepository):
    """
    [보너스 4] 저장 원자성 강화 저장소.
    수정/삭제 시 임시 파일에 기록 후 os.replace로 원자적(Atomic) 교체합니다.
    """

    def _rewrite_all(self, items: List[dict]) -> None:
        temp_file = None
        try:
            # 원자적 교체를 위해 대상 파일과 동일한 디렉터리에 임시 파일 생성
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.data_dir,
                delete=False,
            ) as f:
                temp_file = Path(f.name)
                for item in items:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())

            # 원자적 교체 (atomic rename / replace)
            os.replace(temp_file, self.file_path)
            temp_file = None
        finally:
            if temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                except OSError:
                    pass


class TableFormatter:
    """
    [보너스 3] 외부 라이브러리 없이 콘솔 너비와 유니코드 전각 문자를 고려한 테이블 포맷터.
    """

    @staticmethod
    def _char_width(ch: str) -> int:
        # 동아시아 전각/Wide 문자(한글, 한자 등)는 콘솔 너비 2 차지
        return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1

    @classmethod
    def _str_width(cls, text: str) -> int:
        return sum(cls._char_width(c) for c in str(text))

    @classmethod
    def _pad_string(cls, text: str, width: int, align: str = "left") -> str:
        text_str = str(text)
        current_w = cls._str_width(text_str)
        pad_size = max(0, width - current_w)
        if align == "right":
            return " " * pad_size + text_str
        elif align == "center":
            left_pad = pad_size // 2
            right_pad = pad_size - left_pad
            return " " * left_pad + text_str + " " * right_pad
        return text_str + " " * pad_size

    def format_table(self, headers: list[str], rows: list[list[Any]]) -> str:
        """표 형태의 문자열 생성"""
        if not headers:
            return ""

        col_count = len(headers)
        col_widths = [self._str_width(h) for h in headers]

        # 각 컬럼의 최대 너비 계산
        for row in rows:
            for i in range(min(col_count, len(row))):
                col_widths[i] = max(col_widths[i], self._str_width(row[i]))

        # 경계선 생성
        separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

        # 헤더 라인
        header_cells = [
            f" {self._pad_string(h, col_widths[i], 'center')} " for i, h in enumerate(headers)
        ]
        header_line = "|" + "|".join(header_cells) + "|"

        lines = [separator, header_line, separator]

        # 데이터 라인
        for row in rows:
            cells = []
            for i in range(col_count):
                val = row[i] if i < len(row) else ""
                align = "right" if isinstance(val, (int, float)) else "left"
                cells.append(f" {self._pad_string(val, col_widths[i], align)} ")
            lines.append("|" + "|".join(cells) + "|")

        lines.append(separator)
        return "\n".join(lines)


@dataclass
class RecurringTransaction:
    """반복 거래 규칙 데이터 모델"""

    day: int  # 1 ~ 31
    type: str  # income | expense
    category: str
    amount: int
    memo: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "day": self.day,
            "type": self.type,
            "category": self.category,
            "amount": self.amount,
            "memo": self.memo,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecurringTransaction":
        return cls(
            day=int(data.get("day", 1)),
            type=str(data.get("type", "expense")),
            category=str(data.get("category", "")),
            amount=int(data.get("amount", 0)),
            memo=str(data.get("memo", "") or ""),
            tags=list(data.get("tags", [])),
        )


class RecurringStore:
    """반복 거래 규칙 저장소"""

    def __init__(self, data_dir: Path | str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.data_dir / "recurring.jsonl"

    def get_all(self) -> list[RecurringTransaction]:
        if not self.file_path.exists():
            return []
        items = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    items.append(RecurringTransaction.from_dict(json.loads(line)))
        return items

    def add(self, rule: RecurringTransaction) -> None:
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rule.to_dict(), ensure_ascii=False) + "\n")


class BonusBudgetService(BudgetService):
    """
    [보너스 기능 통합 서비스]
    BudgetService를 상속받아 원자적 저장소, 백업, 반복 거래 생성을 확장 구현합니다.
    """

    def __init__(self, data_dir: Path | str = "./data"):
        super().__init__(data_dir=data_dir)
        # 기본 TransactionRepository를 원자적 저장소로 교체
        self.repo = AtomicTransactionRepository(self.data_dir)
        self.recurring_store = RecurringStore(self.data_dir)

    def create_backup(self, backup_dir: Path | str = "./backups") -> Path:
        """[보너스 1] 타임스탬프 기반 데이터 백업 파일(.zip) 생성"""
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"backup_{timestamp}.zip"
        target_zip = backup_path / zip_filename

        with zipfile.ZipFile(target_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in self.data_dir.glob("*.jsonl"):
                zf.write(file, arcname=file.name)

        return target_zip

    def add_recurring(
        self,
        day: int,
        type_: str,
        category: str,
        amount: int | str,
        memo: str = "",
        tags: Optional[list[str]] = None,
    ) -> RecurringTransaction:
        """[보너스 2] 반복 거래 규칙 등록"""
        if not (1 <= int(day) <= 31):
            raise ValidationError("반복 발생 일(day)은 1부터 31 사이여야 합니다.", hint="예: 25")
        valid_type = validate_type(type_)
        valid_amount = validate_amount(amount)
        clean_cat = (category or "").strip()
        if not self.cat_store.exists(clean_cat):
            raise ValidationError(f"등록되지 않은 카테고리입니다: '{clean_cat}'")

        rule = RecurringTransaction(
            day=int(day),
            type=valid_type,
            category=clean_cat,
            amount=valid_amount,
            memo=memo.strip() if memo else "",
            tags=tags or [],
        )
        self.recurring_store.add(rule)
        return rule

    def list_recurring(self) -> list[RecurringTransaction]:
        """반복 거래 규칙 목록 조회"""
        return self.recurring_store.get_all()

    def generate_recurring(self, month: str) -> list[Transaction]:
        """[보너스 2] 특정 월(YYYY-MM)의 반복 거래 자동 생성"""
        valid_month = validate_month(month)
        rules = self.recurring_store.get_all()
        if not rules:
            return []

        existing = [tx for tx in self.repo.stream_all() if tx.date.startswith(valid_month)]
        created: list[Transaction] = []

        for rule in rules:
            target_date = f"{valid_month}-{min(rule.day, 28):02d}"
            expected_memo = f"[반복] {rule.memo}" if rule.memo else "[반복 거래]"
            # 중복 생성 방지 확인 (해당 월에 동일한 타입, 카테고리, 금액, 메모 거래가 이미 존재하는지 확인)
            is_duplicate = any(
                tx.date.startswith(valid_month)
                and tx.type == rule.type
                and tx.category == rule.category
                and tx.amount == rule.amount
                and (tx.memo == expected_memo or tx.memo == rule.memo)
                for tx in existing
            )
            if not is_duplicate:
                tx = self.add_transaction(
                    date=target_date,
                    type_=rule.type,
                    category=rule.category,
                    amount=rule.amount,
                    memo=expected_memo,
                    tags=rule.tags,
                )
                created.append(tx)
                existing.append(tx)

        return created


class BonusCLI(BudgetCLI):
    """
    [보너스 CLI]
    BudgetCLI를 상속받아 테이블 포맷 출력 및 백업, 반복거래 커맨드를 확장합니다.
    """

    def __init__(self, service: BonusBudgetService):
        super().__init__(service)
        self.bonus_service = service
        self.formatter = TableFormatter()

    def handle_list(self, limit: Optional[int] = None) -> None:
        """거래 목록 테이블 포맷 출력"""
        txs = self.service.list_transactions(limit=limit)
        if not txs:
            print("거래 내역이 없습니다.")
            return

        headers = ["ID", "날짜", "타입", "카테고리", "금액(원)", "메모", "태그"]
        rows = [
            [tx.id, tx.date, tx.type, tx.category, tx.amount, tx.memo, ", ".join(tx.tags)]
            for tx in txs
        ]
        print(self.formatter.format_table(headers, rows))

    def handle_search(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        category: Optional[str] = None,
        type_: Optional[str] = None,
        query: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> None:
        """검색 결과 테이블 포맷 출력"""
        txs = self.service.search_transactions(
            from_date=from_date,
            to_date=to_date,
            category=category,
            type_=type_,
            query=query,
            tag=tag,
        )
        if not txs:
            print("검색 조건에 일치하는 거래가 없습니다.")
            return

        headers = ["ID", "날짜", "타입", "카테고리", "금액(원)", "메모", "태그"]
        rows = [
            [tx.id, tx.date, tx.type, tx.category, tx.amount, tx.memo, ", ".join(tx.tags)]
            for tx in txs
        ]
        print(self.formatter.format_table(headers, rows))

    def handle_backup(self, backup_dir: str = "./backups") -> None:
        """백업 실행"""
        target = self.bonus_service.create_backup(backup_dir=backup_dir)
        print(f"[백업 완료] 백업 파일: {target}")

    def handle_recurring_add(self) -> None:
        """반복 거래 규칙 등록 (대화형)"""
        day = input("반복일(1~31): ").strip()
        type_ = input("타입(income/expense): ").strip()
        category = input("카테고리: ").strip()
        amount = input("금액(양수): ").strip()
        memo = input("메모(선택): ").strip()
        tags_input = input("태그(쉼표로 구분, 없으면 엔터): ").strip()
        tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []

        rule = self.bonus_service.add_recurring(
            day=int(day),
            type_=type_,
            category=category,
            amount=amount,
            memo=memo,
            tags=tags,
        )
        print(f"[저장 완료] 매월 {rule.day}일 {rule.category} {rule.amount}원 등록")

    def handle_recurring_list(self) -> None:
        """반복 거래 규칙 목록"""
        rules = self.bonus_service.list_recurring()
        if not rules:
            print("등록된 반복 거래가 없습니다.")
            return

        headers = ["반복일", "타입", "카테고리", "금액(원)", "메모", "태그"]
        rows = [
            [f"매월 {r.day}일", r.type, r.category, r.amount, r.memo, ", ".join(r.tags)]
            for r in rules
        ]
        print(self.formatter.format_table(headers, rows))

    def handle_recurring_generate(self, month: str) -> None:
        """반복 거래 자동 생성 실행"""
        generated = self.bonus_service.generate_recurring(month=month)
        print(f"[완료] {month}월 반복 거래 {len(generated)}건이 자동 생성되었습니다.")


def build_bonus_parser() -> argparse.ArgumentParser:
    """보너스 기능이 확장된 CLI 파서"""
    parser = build_parser()

    subparsers_action = [
        action for action in parser._actions if isinstance(action, argparse._SubParsersAction)
    ]
    if not subparsers_action:
        return parser

    subparsers = subparsers_action[0]

    # backup
    backup_parser = subparsers.add_parser("backup", help="[보너스] 데이터 디렉터리 타임스탬프 압축 백업")
    backup_parser.add_argument(
        "--backup-dir", default="./backups", help="백업 파일 저장 경로 (기본값: ./backups)"
    )

    # recurring
    rec_parser = subparsers.add_parser("recurring", help="[보너스] 반복 거래 관리")
    rec_sub = rec_parser.add_subparsers(dest="rec_action", help="반복 거래 하위 명령")
    rec_sub.add_parser("add", help="반복 거래 규칙 추가 (대화형)")
    rec_sub.add_parser("list", help="반복 거래 규칙 목록 조회")
    rec_gen = rec_sub.add_parser("generate", help="특정 월의 반복 거래 자동 생성")
    rec_gen.add_argument("--month", required=True, help="생성할 대상 월 (YYYY-MM)")

    return parser


@handle_cli_errors
def main_bonus_cli(args: Optional[Sequence[str]] = None) -> None:
    """보너스 확장 CLI 진입점"""
    parser = build_bonus_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        sys.exit(0)

    service = BonusBudgetService(data_dir=parsed_args.data_dir)
    cli = BonusCLI(service)

    cmd = parsed_args.command
    if cmd == "backup":
        cli.handle_backup(backup_dir=parsed_args.backup_dir)
    elif cmd == "recurring":
        if parsed_args.rec_action == "add":
            cli.handle_recurring_add()
        elif parsed_args.rec_action == "list":
            cli.handle_recurring_list()
        elif parsed_args.rec_action == "generate":
            cli.handle_recurring_generate(month=parsed_args.month)
        else:
            print("[오류] recurring 뒤에 하위 명령어(add/list/generate)가 필요합니다.")
            sys.exit(1)
    else:
        # 기본 명령어 처리 (대신 테이블 뷰와 원자적 저장소 적용)
        if cmd == "add":
            cli.handle_add()
        elif cmd == "list":
            cli.handle_list(limit=parsed_args.limit)
        elif cmd == "search":
            cli.handle_search(
                from_date=parsed_args.from_date,
                to_date=parsed_args.to_date,
                category=parsed_args.category,
                type_=parsed_args.type_,
                query=parsed_args.query,
                tag=parsed_args.tag,
            )
        elif cmd == "summary":
            cli.handle_summary(month=parsed_args.month, top_n=parsed_args.top)
        elif cmd == "budget":
            if parsed_args.budget_action == "set":
                cli.handle_budget_set(month=parsed_args.month, amount=parsed_args.amount)
            else:
                print("[오류] budget 뒤에 하위 명령어가 필요합니다.")
                sys.exit(1)
        elif cmd == "category":
            if parsed_args.cat_action == "add":
                cli.handle_category_add(name=parsed_args.name)
            elif parsed_args.cat_action == "list":
                cli.handle_category_list()
            elif parsed_args.cat_action == "remove":
                cli.handle_category_remove(name=parsed_args.name, replacement=parsed_args.replace)
            else:
                print("[오류] category 뒤에 하위 명령어가 필요합니다.")
                sys.exit(1)
        elif cmd == "update":
            cli.handle_update(
                tx_id=parsed_args.tx_id,
                date=parsed_args.date,
                type_=parsed_args.type_,
                category=parsed_args.category,
                amount=parsed_args.amount,
                memo=parsed_args.memo,
                tags=parsed_args.tags,
            )
        elif cmd == "delete":
            cli.handle_delete(tx_id=parsed_args.tx_id)
        elif cmd == "export":
            cli.handle_export(
                out_file=parsed_args.out,
                month=parsed_args.month,
                from_date=parsed_args.from_date,
                to_date=parsed_args.to_date,
            )
        elif cmd == "import":
            cli.handle_import(from_file=parsed_args.from_file)


if __name__ == "__main__":
    main_bonus_cli()
