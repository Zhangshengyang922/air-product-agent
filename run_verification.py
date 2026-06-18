import subprocess
import sys

# 运行验证脚本
result = subprocess.run(
    [sys.executable, '发布验证.py'],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='ignore'
)

# 保存结果
with open('验证结果.txt', 'w', encoding='utf-8') as f:
    # 过滤掉警告信息
    lines = result.stdout.split('\n')
    filtered_lines = []
    skip_next = False
    for line in lines:
        if 'RequestsDependencyWarning' in line:
            skip_next = True
            continue
        if skip_next and 'warnings.warn' in line:
            continue
        if not line.startswith('  warnings.warn'):
            filtered_lines.append(line)
    f.write('\n'.join(filtered_lines))

print("验证完成，结果已保存到: 验证结果.txt")
