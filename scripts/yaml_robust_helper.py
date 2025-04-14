#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
YAMLロバスト処理ヘルパー
YAMLの処理を安全かつ堅牢に行うための共通ユーティリティ関数
"""

import yaml
import re
from pathlib import Path
import os

def safe_yaml_load(yaml_content, default=None):
    """
    安全にYAMLを読み込む関数
    
    Args:
        yaml_content (str): YAML形式の文字列
        default (dict, optional): 失敗時のデフォルト値。デフォルトは空辞書。
    
    Returns:
        dict: 読み込んだデータか、エラー時にはdefault値
    """
    if default is None:
        default = {}
    
    try:
        data = yaml.safe_load(yaml_content)
        # データが辞書の場合のみ返す
        if isinstance(data, dict):
            return data
        elif data is None:
            return default
        else:
            print(f"YAMLデータが辞書ではありません: {data}")
            return default
    except Exception as e:
        print(f"YAMLパースエラー: {e}")
        return default

def safe_yaml_dump(data, file_obj, **kwargs):
    """
    安全にYAMLを書き込む関数
    
    Args:
        data (dict): 書き込むデータ
        file_obj (file): 書き込み先ファイルオブジェクト
        **kwargs: yaml.dump関数に渡す追加パラメータ
    
    Returns:
        bool: 成功したらTrue、失敗したらFalse
    """
    try:
        yaml.dump(data, file_obj, **kwargs)
        return True
    except Exception as e:
        print(f"YAMLダンプエラー: {e}")
        # エラー時には基本的な形式でデータを出力する
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                file_obj.write(f"{key}: {value}\n")
        return False

def extract_yaml_frontmatter(content):
    """
    マークダウンコンテンツからYAMLフロントマターを抽出
    
    Args:
        content (str): マークダウンコンテンツ
        
    Returns:
        tuple: (yaml_data, rest_of_content) - YAMLデータと残りのコンテンツ
               YAMLフロントマターがない場合は(None, content)
    """
    yaml_pattern = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
    match = yaml_pattern.search(content)
    
    if not match:
        return None, content
    
    yaml_content = match.group(1)
    rest_of_content = content[match.end():].lstrip()
    
    yaml_data = safe_yaml_load(yaml_content)
    return yaml_data, rest_of_content

def extract_title_from_markdown(content):
    """
    マークダウンコンテンツから最初の見出しをタイトルとして抽出
    
    Args:
        content (str): マークダウンコンテンツ
        
    Returns:
        str: 抽出したタイトル、見つからない場合は空文字列
    """
    title_pattern = re.compile(r"^#\s+(.*?)$", re.MULTILINE)
    match = title_pattern.search(content)
    
    if match:
        return match.group(1).strip()
    return ""

def write_markdown_with_frontmatter(file_path, metadata, content):
    """
    マークダウンファイルをフロントマター付きで書き込む
    
    Args:
        file_path (str or Path): 書き込み先ファイルパス
        metadata (dict): YAMLフロントマターとして書き込むメタデータ
        content (str): 本文コンテンツ
        
    Returns:
        bool: 成功したらTrue、失敗したらFalse
    """
    try:
        # ディレクトリが存在しない場合は作成
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("---\n")
            success = safe_yaml_dump(metadata, f, default_flow_style=False, allow_unicode=True)
            f.write("---\n\n")
            f.write(content)
        
        return True
    except Exception as e:
        print(f"ファイル書き込みエラー: {e}")
        return False
