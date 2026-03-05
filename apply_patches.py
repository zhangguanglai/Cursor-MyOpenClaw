"""应用代码补丁到代码库"""

import sys
import io
import subprocess
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def apply_patch(patch_file: Path):
    """应用单个补丁文件"""
    print(f"\n📦 应用补丁: {patch_file.name}")
    
    try:
        # 使用 git apply 应用补丁
        result = subprocess.run(
            ["git", "apply", "--check", str(patch_file)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            # 补丁可以应用
            print(f"   ✅ 补丁检查通过")
            result = subprocess.run(
                ["git", "apply", str(patch_file)],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            if result.returncode == 0:
                print(f"   ✅ 补丁应用成功")
                return True
            else:
                print(f"   ❌ 补丁应用失败: {result.stderr}")
                return False
        else:
            # 补丁可能已经应用或存在冲突
            print(f"   ⚠️  补丁检查失败: {result.stderr}")
            print(f"   ℹ️  可能已经应用或需要手动处理")
            return None
            
    except Exception as e:
        print(f"   ❌ 应用补丁时出错: {e}")
        return False

def main():
    case_id = "case-1fadf9d2"
    patches_dir = Path(f"cases/{case_id}/patches")
    
    if not patches_dir.exists():
        print(f"❌ 补丁目录不存在: {patches_dir}")
        return
    
    # 获取所有补丁文件
    patch_files = sorted(patches_dir.glob("*.patch"))
    
    print("=" * 60)
    print("应用代码补丁")
    print("=" * 60)
    print(f"\n补丁目录: {patches_dir}")
    print(f"补丁数量: {len(patch_files)}")
    print()
    
    if not patch_files:
        print("❌ 没有找到补丁文件")
        return
    
    # 按任务 ID 排序
    patch_files.sort(key=lambda p: p.stem)
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for patch_file in patch_files:
        result = apply_patch(patch_file)
        if result is True:
            success_count += 1
        elif result is False:
            fail_count += 1
        else:
            skip_count += 1
    
    print("\n" + "=" * 60)
    print("补丁应用完成")
    print("=" * 60)
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {fail_count}")
    print(f"⏭️  跳过: {skip_count}")
    print(f"📊 总计: {len(patch_files)}")
    
    if fail_count > 0:
        print("\n⚠️  有补丁应用失败，请手动检查并修复")

if __name__ == "__main__":
    main()
