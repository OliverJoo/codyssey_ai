"""명령줄 인터페이스(CLI) 파싱 및 대화형 입출력 모듈"""

import argparse
import sys
from typing import Optional, Sequence
from budget_app.models import ValidationError
from budget_app.service import BudgetService
from budget_app.decorators import handle_cli_errors


class BudgetCLI:
    """가계부 CLI 핸들러"""

    def __init__(self, service: BudgetService):
        self.service = service

    def handle_add(self) -> None:
        """거래 추가 (대화형 입력)"""
        date_input = input("날짜(YYYY-MM-DD): ").strip()
        type_input = input("타입(income/expense): ").strip()
        category_input = input("카테고리: ").strip()
        amount_input = input("금액(양수): ").strip()
        memo_input = input("메모(선택): ").strip()
        tags_input = input("태그(쉼표로 구분, 없으면 엔터): ").strip()

        tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []
        tx = self.service.add_transaction(
            date=date_input,
            type_=type_input,
            category=category_input,
            amount=amount_input,
            memo=memo_input,
            tags=tags,
        )
        print(f"[저장 완료] id={tx.id}")

    def handle_list(self, limit: Optional[int] = None) -> None:
        """거래 목록 조회"""
        txs = self.service.list_transactions(limit=limit)
        if not txs:
            print("거래 내역이 없습니다.")
            return
        for tx in txs:
            memo_str = f" {tx.memo}" if tx.memo else ""
            print(f"{tx.id} | {tx.date} | {tx.type} | {tx.category} | {tx.amount} |{memo_str}")

    def handle_search(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        category: Optional[str] = None,
        type_: Optional[str] = None,
        query: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> None:
        """거래 조건 검색"""
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
        for tx in txs:
            memo_str = f" {tx.memo}" if tx.memo else ""
            print(f"{tx.id} | {tx.date} | {tx.type} | {tx.category} | {tx.amount} |{memo_str}")

    def handle_summary(self, month: str, top_n: int = 3) -> None:
        """월별 요약 리포트"""
        res = self.service.get_monthly_summary(month=month, top_n=top_n)
        if not res["has_data"]:
            print(f"{month} 데이터 없음")
            return

        print(f"총 수입: {res['total_income']}원")
        print(f"총 지출: {res['total_expense']}원")
        print(f"잔액: {res['balance']}원")

        if res["budget_amount"] is not None:
            usage_str = f"예산: {res['budget_amount']}원 (사용률 {res['usage_rate']}%)"
            print(usage_str)
            if res["is_over_budget"]:
                over_amount = res["total_expense"] - res["budget_amount"]
                print(f"[경고] 예산을 초과했습니다! (초과액: {over_amount}원)")

        if res["top_expenses"]:
            print(f"\n지출 TOP {len(res['top_expenses'])}")
            for idx, (cat, amt) in enumerate(res["top_expenses"], 1):
                print(f"{idx}) {cat} {amt}원")

    def handle_budget_set(self, month: str, amount: int | str) -> None:
        """예산 설정"""
        b = self.service.set_budget(month=month, amount=amount)
        print(f"[저장 완료] {b.month} 예산 {b.amount}원")

    def handle_category_add(self, name: Optional[str] = None) -> None:
        """카테고리 추가"""
        if not name:
            name = input("카테고리명: ").strip()
        self.service.category_add(name)
        print(f"[저장 완료] category={name}")

    def handle_category_list(self) -> None:
        """카테고리 목록"""
        cats = self.service.category_list()
        for cat in cats:
            print(f"- {cat}")

    def handle_category_remove(self, name: str, replacement: Optional[str] = None) -> None:
        """카테고리 삭제"""
        self.service.category_remove(name, replacement=replacement)
        print(f"[삭제 완료] category={name}")

    def handle_update(
        self,
        tx_id: str,
        date: Optional[str] = None,
        type_: Optional[str] = None,
        category: Optional[str] = None,
        amount: Optional[int | str] = None,
        memo: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> None:
        """거래 수정 (옵션 방식)"""
        parsed_tags = (
            [t.strip() for t in tags.split(",") if t.strip()] if tags is not None else None
        )
        tx = self.service.update_transaction(
            tx_id=tx_id,
            date=date,
            type_=type_,
            category=category,
            amount=amount,
            memo=memo,
            tags=parsed_tags,
        )
        print(f"[수정 완료] id={tx.id}")

    def handle_delete(self, tx_id: str) -> None:
        """거래 삭제"""
        self.service.delete_transaction(tx_id)
        print(f"[삭제 완료] id={tx_id}")

    def handle_export(
        self,
        out_file: str,
        month: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> None:
        """CSV 내보내기"""
        count = self.service.export_to_csv(
            filepath=out_file, month=month, from_date=from_date, to_date=to_date
        )
        print(f"[완료] {out_file} ({count} records)")

    def handle_import(self, from_file: str) -> None:
        """CSV 가져오기"""
        imported, skipped = self.service.import_from_csv(filepath=from_file)
        print(f"[완료] imported={imported}, skipped={skipped}")


def build_parser() -> argparse.ArgumentParser:
    """CLI 인자 파서 생성"""
    parser = argparse.ArgumentParser(
        prog="budget_app",
        description="나만의 용돈 기입장 콘솔 프로그램",
    )
    parser.add_argument(
        "--data-dir",
        default="./data",
        help="데이터 저장 디렉터리 경로 (기본값: ./data)",
    )

    subparsers = parser.add_subparsers(dest="command", help="실행할 명령")

    # add
    subparsers.add_parser("add", help="신규 거래 추가 (대화형 입력)")

    # list
    list_parser = subparsers.add_parser("list", help="거래 목록 최신순 조회")
    list_parser.add_argument("--limit", type=int, default=None, help="출력할 최대 거래 건수")

    # search
    search_parser = subparsers.add_parser("search", help="조건 기반 거래 검색")
    search_parser.add_argument("--from", dest="from_date", help="시작 날짜 (YYYY-MM-DD)")
    search_parser.add_argument("--to", dest="to_date", help="종료 날짜 (YYYY-MM-DD)")
    search_parser.add_argument("--category", help="카테고리")
    search_parser.add_argument("--type", dest="type_", help="타입 (income / expense)")
    search_parser.add_argument("--q", dest="query", help="메모/카테고리/ID 검색 키워드")
    search_parser.add_argument("--tag", help="태그")

    # summary
    summary_parser = subparsers.add_parser("summary", help="월별 통계 요약")
    summary_parser.add_argument("--month", required=True, help="조회할 월 (YYYY-MM)")
    summary_parser.add_argument("--top", type=int, default=3, help="지출 상위 카테고리 수 (기본값: 3)")

    # budget
    budget_parser = subparsers.add_parser("budget", help="예산 관리")
    budget_sub = budget_parser.add_subparsers(dest="budget_action", help="예산 세부 명령")
    b_set = budget_sub.add_parser("set", help="월별 예산 설정")
    b_set.add_argument("--month", required=True, help="예산 대상 월 (YYYY-MM)")
    b_set.add_argument("--amount", required=True, type=int, help="예산 금액 (원)")

    # category
    cat_parser = subparsers.add_parser("category", help="카테고리 관리")
    cat_sub = cat_parser.add_subparsers(dest="cat_action", help="카테고리 세부 명령")
    cat_add = cat_sub.add_parser("add", help="카테고리 추가")
    cat_add.add_argument("name", nargs="?", default=None, help="카테고리명 (생략 시 대화형 입력)")
    cat_sub.add_parser("list", help="카테고리 목록 조회")
    cat_rem = cat_sub.add_parser("remove", help="카테고리 삭제")
    cat_rem.add_argument("name", help="삭제할 카테고리명")
    cat_rem.add_argument("--replace", help="기존 거래 내역을 대체할 카테고리명")

    # update
    upd_parser = subparsers.add_parser("update", help="거래 내역 수정")
    upd_parser.add_argument("--id", dest="tx_id", required=True, help="수정할 거래 ID")
    upd_parser.add_argument("--date", help="새 날짜 (YYYY-MM-DD)")
    upd_parser.add_argument("--type", dest="type_", help="새 타입 (income / expense)")
    upd_parser.add_argument("--category", help="새 카테고리")
    upd_parser.add_argument("--amount", type=int, help="새 금액")
    upd_parser.add_argument("--memo", help="새 메모")
    upd_parser.add_argument("--tags", help="새 태그 (쉼표 구분)")

    # delete
    del_parser = subparsers.add_parser("delete", help="거래 내역 삭제")
    del_parser.add_argument("--id", dest="tx_id", required=True, help="삭제할 거래 ID")

    # export
    exp_parser = subparsers.add_parser("export", help="거래 내역 CSV 파일로 내보내기")
    exp_parser.add_argument("--out", required=True, help="내보낼 CSV 파일 경로")
    exp_parser.add_argument("--month", help="내보낼 월 (YYYY-MM)")
    exp_parser.add_argument("--from", dest="from_date", help="시작 날짜 (YYYY-MM-DD)")
    exp_parser.add_argument("--to", dest="to_date", help="종료 날짜 (YYYY-MM-DD)")

    # import
    imp_parser = subparsers.add_parser("import", help="CSV 파일에서 거래 내역 가져오기")
    imp_parser.add_argument("--from", dest="from_file", required=True, help="가져올 CSV 파일 경로")

    return parser


@handle_cli_errors
def main_cli(args: Optional[Sequence[str]] = None) -> None:
    """CLI 진입점 함수"""
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        sys.exit(0)

    service = BudgetService(data_dir=parsed_args.data_dir)
    cli = BudgetCLI(service)

    cmd = parsed_args.command
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
            print("[오류] budget 뒤에 하위 명령어(set)가 필요합니다.")
            sys.exit(1)
    elif cmd == "category":
        if parsed_args.cat_action == "add":
            cli.handle_category_add(name=parsed_args.name)
        elif parsed_args.cat_action == "list":
            cli.handle_category_list()
        elif parsed_args.cat_action == "remove":
            cli.handle_category_remove(name=parsed_args.name, replacement=parsed_args.replace)
        else:
            print("[오류] category 뒤에 하위 명령어(add/list/remove)가 필요합니다.")
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
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main_cli()
