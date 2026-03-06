#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试补丁应用功能
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"
CASE_ID = "case-e13da6ed"

def test_get_patches():
    """测试获取补丁列表"""
    print("=" * 60)
    print("Test 1: Get Patches")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/cases/{CASE_ID}/patches", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            patches = response.json()
            print(f"Found {len(patches)} patches")
            if patches:
                print("\nPatches:")
                for i, patch in enumerate(patches[:3], 1):
                    print(f"  {i}. Task: {patch.get('task_id', 'N/A')}")
                    print(f"     File: {patch.get('file_path', 'N/A')}")
                    print(f"     Description: {patch.get('description', 'N/A')[:50]}...")
            return patches
        else:
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def test_apply_patch_dry_run(patch_id):
    """测试补丁应用（试运行）"""
    print("\n" + "=" * 60)
    print("Test 2: Apply Patch (Dry Run)")
    print("=" * 60)
    print(f"Patch ID: {patch_id}")
    
    # 注意：当前 API 不支持 dry_run 参数，这里只是测试 API 调用
    try:
        response = requests.patch(
            f"{BASE_URL}/cases/{CASE_ID}/patches/{patch_id}/apply",
            params={"commit": False},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Patch applied")
            print(f"Message: {result.get('message', 'N/A')}")
            print(f"Result: {result.get('result', 'N/A')}")
            if result.get('details'):
                files = result['details'].get('files', [])
                print(f"Files affected: {len(files)}")
                for f in files:
                    print(f"  - {f.get('file_path', 'N/A')}: {f.get('status', 'N/A')}")
            return True
        elif response.status_code == 409:
            print("CONFLICT: Patch has conflicts")
            try:
                error = response.json()
                print(f"Detail: {error.get('detail', 'N/A')}")
            except:
                print(f"Response: {response.text[:200]}")
            return False
        else:
            print(f"ERROR: {response.status_code}")
            try:
                error = response.json()
                print(f"Detail: {error.get('detail', 'N/A')}")
            except:
                print(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_apply_patch_with_commit(patch_id):
    """测试补丁应用并提交到 Git"""
    print("\n" + "=" * 60)
    print("Test 3: Apply Patch with Git Commit")
    print("=" * 60)
    print(f"Patch ID: {patch_id}")
    print("NOTE: This will actually apply the patch and commit to Git!")
    print("Skipping for safety...")
    return True

def main():
    print("=" * 60)
    print("Patch Apply Functionality Test")
    print("=" * 60)
    print(f"\nCase ID: {CASE_ID}")
    
    # Test 1: Get patches
    patches = test_get_patches()
    
    if not patches:
        print("\nNo patches found. Please generate patches first.")
        return
    
    # Test 2: Apply patch (dry run)
    patch_id = patches[0].get('task_id') or patches[0].get('id')
    if patch_id:
        print(f"\nUsing first patch: {patch_id}")
        # 注意：实际应用中，我们应该先检查补丁格式
        # 这里只是测试 API 是否正常工作
        print("\n⚠️  WARNING: This will actually apply the patch to the codebase!")
        print("Skipping actual application for safety.")
        print("To test, manually call the API or use a test repository.")
    else:
        print("\nNo valid patch ID found")
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print("[OK] Get patches: OK")
    print("[SKIP] Apply patch: Skipped (safety)")
    print("[SKIP] Apply with commit: Skipped (safety)")
    print("\nTo fully test:")
    print("1. Use a test repository")
    print("2. Generate a test patch")
    print("3. Apply the patch via API")
    print("4. Verify the changes")

if __name__ == "__main__":
    main()
