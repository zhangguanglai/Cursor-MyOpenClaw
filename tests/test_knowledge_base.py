"""
知识库测试
"""

import pytest
import tempfile
from pathlib import Path
from openclaw_studio.knowledge_base import KnowledgeBase, KnowledgeItem


@pytest.fixture
def temp_kb():
    """创建临时知识库"""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb = KnowledgeBase(base_path=tmpdir)
        yield kb


def test_knowledge_base_init(temp_kb):
    """测试知识库初始化"""
    assert temp_kb.base_path.exists()
    assert (temp_kb.base_path / "rules").exists()
    assert (temp_kb.base_path / "playbooks").exists()
    assert (temp_kb.base_path / "templates").exists()
    assert (temp_kb.base_path / "cases").exists()


def test_create_template(temp_kb):
    """测试创建模板"""
    template_content = "# Test Template\n\nThis is a test template."
    template_path = temp_kb.base_path / "templates" / "test_template.md"
    template_path.write_text(template_content)
    
    templates = temp_kb.list_templates()
    assert "test_template" in templates


def test_get_template(temp_kb):
    """测试获取模板"""
    template_content = "# Test Template\n\nThis is a test template."
    template_path = temp_kb.base_path / "templates" / "test_template.md"
    template_path.write_text(template_content)
    
    content = temp_kb.get_template("test_template")
    assert content == template_content


def test_search(temp_kb):
    """测试搜索功能"""
    # 创建测试文件
    test_file = temp_kb.base_path / "rules" / "test_rule.md"
    test_file.write_text("# Test Rule\n\nThis is a test rule about Python.")
    
    results = temp_kb.search("Python")
    assert len(results) > 0
    assert any("Python" in item.content for item in results)


def test_search_by_category(temp_kb):
    """测试按类别搜索"""
    # 创建不同类别的文件
    rule_file = temp_kb.base_path / "rules" / "rule.md"
    rule_file.write_text("# Rule\n\nRule content.")
    
    playbook_file = temp_kb.base_path / "playbooks" / "playbook.md"
    playbook_file.write_text("# Playbook\n\nPlaybook content.")
    
    results = temp_kb.search("content", category="rules")
    assert all(item.category == "rules" for item in results)


def test_archive_case(temp_kb):
    """测试归档案例"""
    import tempfile as tf
    
    with tf.TemporaryDirectory() as case_dir:
        case_path = Path(case_dir)
        test_file = case_path / "plan.md"
        test_file.write_text("# Plan\n\nTest plan.")
        
        success = temp_kb.archive_case("test-case-001", case_path)
        assert success
        
        archive_path = temp_kb.base_path / "cases" / "test-case-001" / "plan.md"
        assert archive_path.exists()


def test_list_items(temp_kb):
    """测试列出知识库项"""
    # 创建测试文件
    test_file = temp_kb.base_path / "rules" / "test.md"
    test_file.write_text("# Test\n\nTest content.")
    
    items = temp_kb.list_items(category="rules")
    assert len(items) > 0
    assert all(item.category == "rules" for item in items)
