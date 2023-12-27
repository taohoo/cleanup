# -*- coding: utf-8 -*-
"""
@author: hubo
@project: bb-py
@file: main.py
@time: 2023/11/27 11:44
@desc:
"""
import os
import re
import argparse
import warnings

from environs import Env

from ._cleanup import _format_pattern
from .cleanup import cleanup


def _str_2_list(s):
    return [i.strip() for i in s.split(',')]


def _warn(dir_patterns, file_patterns, exclude_patterns):
    """检测无效配置，给一些建议"""
    cwd = './'.replace('/', os.sep)
    re_pattern = os.sep.replace('\\', '\\\\')
    for path_pattern in dir_patterns + file_patterns + exclude_patterns:
        path_pattern = _format_pattern(path_pattern)
        # 不是以cwd或者*开头，但是包含了os.sep是无法匹配的
        if (not path_pattern.startswith(cwd) and not path_pattern.startswith('*')
                and len(re.findall(re_pattern, path_pattern)) >= 1):
            _path_pattern = os.path.normpath(path_pattern)
            maybes = f"{cwd}{_path_pattern} *{_path_pattern}"
            # 可能多添加了os.sep或者*
            maybes = maybes.replace(f"{os.sep}{os.sep}", f"{os.sep}").replace('**', '*')
            warnings.warn(f"{path_pattern} is invalid. Maybe you want: {maybes}")
        # 以os.sep结尾是无法匹配的
        elif path_pattern.endswith(os.sep):
            warnings.warn(f"{path_pattern} is invalid. Maybe you want: {path_pattern[:-1]}")


def main():
    """
    pip install之后可以通过命令行直接执行，方便进行清理操作
    指令配置在setup.py中。
    :return:
    """
    parser = argparse.ArgumentParser(description='Clean up the current folder')
    parser.add_argument('config_file', nargs='?', type=str, default='.cleanup', help='Configuration file, default to .cleanup in the current working directory')
    parser.add_argument('-d', '--dir_patterns', default='',
                        help='Matching expressions for folders, using Unix Shell style. If there are multiple expressions, use commas to separate them')
    parser.add_argument('-f', '--file_patterns', default='',
                        help='Match expressions for files, using Unix Shell style. If there are multiple expressions, use commas to separate them')
    parser.add_argument('-e', '--exclude_patterns', default='',
                        help='Match expressions for files or folders that are not cleaned, using Unix Shell style. If there are multiple expressions, use commas to separate them')
    args = parser.parse_args()

    dir_patterns = [] if args.dir_patterns == '' else _str_2_list(args.dir_patterns)
    file_patterns = [] if args.file_patterns == '' else _str_2_list(args.file_patterns)
    exclude_patterns = [] if args.exclude_patterns == '' else _str_2_list(args.exclude_patterns)

    # 检查配置文件是否存在
    if os.path.exists(args.config_file):
        if len(dir_patterns) or len(file_patterns) or len(exclude_patterns):
            print(f"{args.config_file} exists, the args in command are ignored.")
        env = Env()
        env.read_env(args.config_file)
        # environs中的strip好像只针对原始配置中的字符串，而不针对解析为list之后的字符元素
        dir_patterns = _str_2_list(env.str('dir_patterns', strip=True))
        file_patterns = _str_2_list(env.str('file_patterns', strip=True))
        exclude_patterns = _str_2_list(env.str('exclude_patterns', strip=True))
    if len(dir_patterns) == 0 and len(file_patterns) == 0 and len(exclude_patterns) == 0:
        parser.print_help()
        exit(0)
    _warn(dir_patterns, file_patterns, exclude_patterns)
    cleanup(dir_patterns, file_patterns, exclude_patterns)
