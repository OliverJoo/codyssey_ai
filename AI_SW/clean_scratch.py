#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Antigravity IDE 임시(Scratch) 파일 정리 스크립트

이 프로그램은 AI 에이전트가 작업 또는 리뷰 과정 중 ~/.gemini/antigravity-ide/brain/
경로 하위의 scratch 폴더들에 임시로 생성한 파일들을 검색하고 안전하게 선택적으로 삭제할 수 있도록 도와줍니다.

[주요 기능]
1. ~/.gemini/antigravity-ide/brain/*/scratch 경로를 탐색하여 모든 임시 파일 수집
2. 수정 시간, 파일 크기를 포함한 미학적인 표(Table) 형태로 터미널 출력
3. 개별 번호 입력(예: 1, 3, 5), 전체 선택('all'), 또는 취소 기능 제공
4. 삭제 실행 전 예상 해제 용량 및 대상 목록 재확인(Y/N) 절차 진행
5. 외장 라이브러리 설치 없이 기본 Python Standard Library만 사용하여 실행 가능
"""

import os
import sys
from datetime import datetime

# 터미널 가독성을 높이기 위한 ANSI escape code 색상 정의
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def format_size(size_bytes):
    """
    파일의 바이트(Byte) 크기를 가독성이 좋은 단위(B, KB, MB)로 변환합니다.
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def get_scratch_files(brain_dir):
    """
    에이전트의 brain 폴더 하위의 모든 scratch 폴더 내 파일들을 재귀적으로 수집합니다.
    
    :param brain_dir: brain 폴더의 절대 경로
    :return: 파일 정보를 담은 딕셔너리들의 리스트
    """
    scratch_files = []
    if not os.path.exists(brain_dir):
        return scratch_files

    # brain 디렉토리 안의 대화 세션 폴더(UUID 형태)들을 순회
    for session_name in os.listdir(brain_dir):
        session_path = os.path.join(brain_dir, session_name)
        if os.path.isdir(session_path):
            scratch_path = os.path.join(session_path, 'scratch')
            # scratch 폴더가 실제로 존재하고 디렉토리인 경우에만 탐색
            if os.path.exists(scratch_path) and os.path.isdir(scratch_path):
                for root, _, files in os.walk(scratch_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            # 파일 정보 추출
                            stat = os.stat(file_path)
                            rel_path = os.path.relpath(file_path, brain_dir)
                            scratch_files.append({
                                'abs_path': file_path,
                                'rel_path': rel_path,
                                'size': stat.st_size,
                                'mtime': stat.st_mtime
                            })
                        except Exception:
                            # 권한 오류 등으로 파일 메타데이터를 읽지 못한 경우는 제외
                            pass
    return scratch_files

def main():
    # 프로그램 타이틀 출력
    print(f"{Colors.BOLD}{Colors.OKBLUE}=== Antigravity IDE 임시(Scratch) 파일 정리 프로그램 ==={Colors.ENDC}\n")

    # 기본 Antigravity IDE의 brain 디렉토리 경로 (~/.gemini/antigravity-ide/brain)
    brain_dir = os.path.expanduser('~/.gemini/antigravity-ide/brain')
    
    if not os.path.exists(brain_dir):
        print(f"{Colors.FAIL}오류: brain 디렉토리를 찾을 수 없습니다.{Colors.ENDC}")
        print(f"예상 경로: {brain_dir}")
        return

    print("임시 파일을 검색하는 중입니다...")
    files = get_scratch_files(brain_dir)

    # 검색된 임시 파일이 없는 경우
    if not files:
        print(f"\n{Colors.OKGREEN}정리할 임시 파일이 존재하지 않습니다. 시스템이 깨끗합니다!{Colors.ENDC}")
        return

    # 최근 수정된 순서(최신 파일이 상위)로 정렬
    files.sort(key=lambda x: x['mtime'], reverse=True)

    # 파일 정보 표(Table) 포맷 출력
    print(f"\n총 {Colors.BOLD}{len(files)}{Colors.ENDC}개의 임시 파일이 발견되었습니다:\n")
    print("=" * 100)
    print(f" {Colors.BOLD}{'번호':<5} | {'파일명 (brain/ 하위 경로)':<50} | {'크기':<12} | {'수정 시간':<19}{Colors.ENDC}")
    print("=" * 100)

    for idx, f_info in enumerate(files, 1):
        mtime_str = datetime.fromtimestamp(f_info['mtime']).strftime('%Y-%m-%d %H:%M:%S')
        size_str = format_size(f_info['size'])
        
        # 파일 경로명이 너무 길면 포맷이 깨지지 않도록 적절히 생략 처리
        rel_path = f_info['rel_path']
        if len(rel_path) > 48:
            parts = rel_path.split(os.sep)
            if len(parts) >= 3:
                # 앞 세션 ID는 일부만 노출하고 뒷부분 경로는 보존
                rel_path = f"{parts[0][:8]}.../{os.sep.join(parts[1:])}"
                if len(rel_path) > 48:
                    rel_path = rel_path[:45] + "..."

        print(f" [{idx:<3}] | {rel_path:<50} | {size_str:<12} | {mtime_str:<19}")
    print("=" * 100)

    # 사용자 동작 입력
    try:
        user_input = input(
            f"\n{Colors.BOLD}삭제할 파일 번호를 선택해 주세요.{Colors.ENDC}\n"
            f"- 특정 파일 삭제: 번호 입력 (예: 1 또는 1,2,5)\n"
            f"- 전체 파일 삭제: 'all' 입력\n"
            f"- 종료: 'q' 또는 Enter 입력\n"
            f"선택: "
        ).strip().lower()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}작업이 사용자 요청으로 취소되었습니다.{Colors.ENDC}")
        return

    # 종료 조건
    if not user_input or user_input in ['q', 'quit', 'exit']:
        print(f"{Colors.WARNING}프로그램을 종료합니다.{Colors.ENDC}")
        return

    targets_to_delete = []

    # 전체 선택 처리
    if user_input == 'all':
        targets_to_delete = files
    else:
        # 특정 파일 선택 처리
        try:
            # 쉼표(,)를 기준으로 분리 후 공백 제거 및 정수 변환
            indices = [int(x.strip()) for x in user_input.split(',') if x.strip()]
            for idx in indices:
                if 1 <= idx <= len(files):
                    targets_to_delete.append(files[idx - 1])
                else:
                    print(f"{Colors.FAIL}경고: 범위를 벗어난 번호({idx})는 무시됩니다.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}오류: 올바르지 않은 입력 형식입니다. 프로그램을 종료합니다.{Colors.ENDC}")
            return

    # 삭제 대상이 없는 경우
    if not targets_to_delete:
        print(f"{Colors.WARNING}삭제할 파일이 선택되지 않았습니다.{Colors.ENDC}")
        return

    # 삭제 전 2차 검증(Confirmation) 출력
    total_freed_bytes = sum(f['size'] for f in targets_to_delete)
    print(f"\n{Colors.BOLD}{Colors.WARNING}=== 삭제 확인 ==={Colors.ENDC}")
    print(f"선택된 파일 개수: {Colors.BOLD}{len(targets_to_delete)}{Colors.ENDC}개")
    print(f"해제될 예상 용량: {Colors.BOLD}{format_size(total_freed_bytes)}{Colors.ENDC}")
    
    # 너무 많을 경우 상위 5개만 목록을 노출
    print("삭제 대상 파일:")
    if len(targets_to_delete) <= 5:
        for t in targets_to_delete:
            print(f"  - {t['rel_path']}")
    else:
        for t in targets_to_delete[:5]:
            print(f"  - {t['rel_path']}")
        print(f"  ... 외 {len(targets_to_delete) - 5}개 파일")

    # 최종 의사결정 확인
    confirm = input(f"\n{Colors.BOLD}{Colors.FAIL}정말로 이 파일들을 삭제하시겠습니까? (y/N): {Colors.ENDC}").strip().lower()
    if confirm != 'y':
        print(f"{Colors.WARNING}삭제 작업이 취소되었습니다.{Colors.ENDC}")
        return

    # 실제 파일 삭제 진행
    deleted_count = 0
    failed_count = 0
    
    print("\n파일을 삭제하는 중...")
    for t in targets_to_delete:
        try:
            os.remove(t['abs_path'])
            deleted_count += 1
        except Exception as e:
            print(f"{Colors.FAIL}삭제 실패: {t['rel_path']} (이유: {e}){Colors.ENDC}")
            failed_count += 1

    # 최종 결과 보고
    print(f"\n{Colors.OKGREEN}정리 완료!{Colors.ENDC}")
    print(f"- 성공: {deleted_count}개 파일")
    if failed_count > 0:
        print(f"- 실패: {failed_count}개 파일")
    print(f"- 확보된 용량: {Colors.BOLD}{format_size(total_freed_bytes)}{Colors.ENDC}")

if __name__ == '__main__':
    main()
