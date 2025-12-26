"""测试IMAP UTF-7编码"""
import codecs

def imap_utf7_encode(s: str) -> str:
    """编码为IMAP UTF-7格式"""
    if not s:
        return s
    try:
        # 将整个字符串编码为UTF-7
        utf7_bytes = s.encode('utf-7')
        utf7_str = utf7_bytes.decode('ascii')
        # 转换标准UTF-7到IMAP UTF-7: + -> &, / -> ,
        result = utf7_str.replace('+', '&').replace('/', ',')
        return result
    except Exception as e:
        print(f"编码错误: {e}")
        return s

# 测试
test_names = ["测试", "我的文件夹", "工作邮件", "test", "Test123"]

print("IMAP UTF-7 编码测试:")
print("=" * 50)
for name in test_names:
    encoded = imap_utf7_encode(name)
    print(f"  '{name}' -> '{encoded}'")
