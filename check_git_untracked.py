#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测父文件夹下的所有git项目，并统计每个项目的untracked files
"""

import os
import subprocess
from pathlib import Path


def is_git_repo(folder_path):
    """检查文件夹是否是git仓库"""
    git_dir = os.path.join(folder_path, '.git')
    return os.path.isdir(git_dir)


def get_untracked_files(repo_path):
    """获取git仓库中的untracked files"""
    try:
        # 运行 git status 命令
        result = subprocess.run(
            ['git', 'status'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode != 0:
            return None

        output = result.stdout
        untracked_files = []

        # 解析输出，查找 Untracked files 部分
        lines = output.split('\n')
        in_untracked_section = False

        for line in lines:
            # 检测 Untracked files 开始
            if 'Untracked files:' in line:
                in_untracked_section = True
                continue

            # 检测 Untracked files 结束
            if in_untracked_section:
                # 空行或其他section开始，结束untracked section
                if line.strip() == '' or (not line.startswith('\t') and not line.startswith('  ')):
                    # 检查是否是提示信息
                    if 'use "git add' in line.lower() or 'include in what will be committed' in line.lower():
                        continue
                    else:
                        break

                # 提取文件名（去掉前面的空格/制表符）
                stripped = line.strip()
                if stripped and not stripped.startswith('('):
                    untracked_files.append(stripped)

        return untracked_files if untracked_files else None

    except Exception as e:
        print(f"错误: 无法检查 {repo_path}: {e}")
        return None


def main():
    # 获取脚本所在目录的父目录
    script_dir = Path(__file__).resolve().parent
    parent_dir = script_dir.parent

    print(f"扫描目录: {parent_dir}")
    print("=" * 80)
    print()

    git_repos = []
    repos_with_untracked = []
    total_untracked_count = 0

    # 遍历父目录下的所有子文件夹
    try:
        for item in os.listdir(parent_dir):
            item_path = os.path.join(parent_dir, item)

            # 只检查文件夹
            if not os.path.isdir(item_path):
                continue

            # 检查是否是git仓库
            if is_git_repo(item_path):
                git_repos.append(item)

                # 获取untracked files
                untracked_files = get_untracked_files(item_path)

                if untracked_files:
                    repos_with_untracked.append({
                        'name': item,
                        'path': item_path,
                        'files': untracked_files
                    })
                    total_untracked_count += len(untracked_files)

    except Exception as e:
        print(f"错误: {e}")
        return

    # 输出结果
    print(f"找到 {len(git_repos)} 个 Git 仓库")
    print(f"其中 {len(repos_with_untracked)} 个仓库有 untracked files")
    print()

    if repos_with_untracked:
        print("=" * 80)
        print("有 Untracked Files 的仓库详情:")
        print("=" * 80)
        print()

        for repo in repos_with_untracked:
            print(f"📁 {repo['name']}")
            print(f"   路径: {repo['path']}")
            print(f"   Untracked files 数量: {len(repo['files'])}")
            print(f"   文件列表:")
            for file in repo['files']:
                print(f"      - {file}")
            print()

        print("=" * 80)
        print(f"总计: {total_untracked_count} 个 untracked files")
        print("=" * 80)
    else:
        print("✓ 所有Git仓库都没有untracked files")


if __name__ == '__main__':
    main()
