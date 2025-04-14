#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
YAMLエラー修正スクリプト
不正なYAMLフロントマターを検出し修正します
"""

import os
import sys
import re
import yaml

def scan_md_files(directory):
    """Markdownファイルを再帰的に検索"""
    md_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                md_files.append(os.path.join(root, file))
    return md_files

def check_yaml_frontmatter(file_path):
    """YAMLフロントマターをチェック"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # YAMLフロントマターのパターン
    yaml_pattern = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
    match = yaml_pattern.search(content)
    
    if not match:
        # YAMLフロントマターがない場合はエラーではない
        return True, None, content
    
    yaml_content = match.group(1)
    
    # YAMLのパースを試みる
    try:
        yaml_data = yaml.safe_load(yaml_content)
        return True, yaml_data, content
    except Exception as e:
        return False, str(e), content

def main():
    """メイン実行関数"""
    print("YAMLエラー修正を開始します...")
    
    # 検査対象ディレクトリ
    directories = ["memory", "theory", "signals", "shells", "dreams"]
    
    all_md_files = []
    for directory in directories:
        if os.path.exists(directory):
            all_md_files.extend(scan_md_files(directory))
    
    print(f"{len(all_md_files)}個のMarkdownファイルをスキャンします")
    
    error_files = []
    for file_path in all_md_files:
        valid, error_or_data, content = check_yaml_frontmatter(file_path)
        if not valid:
            error_files.append((file_path, error_or_data))
            print(f"エラー検出: {file_path} - {error_or_data}")
    
    print(f"{len(error_files)}個のファイルにYAMLエラーが見つかりました")
    
    if error_files:
        print("エラーのあるファイル:")
        for file_path, error in error_files:
            print(f"  {file_path}: {error}")
    else:
        print("すべてのファイルが正常です")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
