#!/usr/bin/env python3
import re
import sys

def swap_isa_and_cflags(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # 正则匹配 isa 赋值行（可包含前后空格）
    isa_pattern = re.compile(r'^\s*isa_arch_list\s*=\s*parse_arch_string\(arch_string\)\s*$', re.MULTILINE)
    # 匹配编译选项块（从第一个 add_asflags 到最后一个 add_cxflags）
    cflags_pattern = re.compile(
        r'^\s*add_asflags\(\'-nostartfiles\'\)\s*\n'
        r'^\s*add_asflags\(\'-march=\' \.\. arch_string\)\s*\n'
        r'^\s*add_asflags\(\'-mabi=ilp32\'\)\s*\n'
        r'^\s*add_cxflags\(\'-march=\' \.\. arch_string\)\s*\n'
        r'^\s*add_cxflags\(\'-mabi=ilp32\'\)\s*\n'
        r'^\s*add_cxflags\("-ffunction-sections",\s*"-fdata-sections",\s*"-fomit-frame-pointer"\)\s*$',
        re.MULTILINE
    )

    isa_match = isa_pattern.search(content)
    cflags_match = cflags_pattern.search(content)

    if not isa_match or not cflags_match:
        print("Error: Could not find isa block or cflags block in the file.")
        sys.exit(1)

    # 获取两个块的位置
    isa_start, isa_end = isa_match.start(), isa_match.end()
    cflags_start, cflags_end = cflags_match.start(), cflags_match.end()

    # 判断当前顺序
    isa_before_cflags = isa_start < cflags_start
    print(f"Current order: {'isa → cflags' if isa_before_cflags else 'cflags → isa'}")

    # 交换两个块（无论当前顺序如何）
    # 提取两个块的文本
    isa_block = content[isa_start:isa_end]
    cflags_block = content[cflags_start:cflags_end]

    # 构造新内容：将两个块互换
    if isa_before_cflags:
        # 原顺序：... isa ... cflags ...
        new_content = (
            content[:isa_start]
            + cflags_block
            + content[isa_end:cflags_start]
            + isa_block
            + content[cflags_end:]
        )
    else:
        # 原顺序：... cflags ... isa ...
        new_content = (
            content[:cflags_start]
            + isa_block
            + content[cflags_end:isa_start]
            + cflags_block
            + content[isa_end:]
        )

    # 写回文件
    with open(filepath, 'w') as f:
        f.write(new_content)

    print("Swap completed. New order: {} → {}".format(
        'cflags' if isa_before_cflags else 'isa',
        'isa' if isa_before_cflags else 'cflags'
    ))

if __name__ == "__main__":
    swap_isa_and_cflags("toolchain.lua")