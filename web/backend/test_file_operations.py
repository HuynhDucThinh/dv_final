"""
Test script cho Phase 1 MVP - Agentic AI File Management System.

Tests:
1. File Manager Service - 6 operations
2. Approval Workflow - Pending actions queue
3. Security validation
4. End-to-end workflow simulation

Run: python test_file_operations.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_file_manager():
    """Test 6 file operations."""
    from app.services import file_manager
    
    logger.info("=" * 60)
    logger.info("TEST 1: File Manager Service")
    logger.info("=" * 60)
    
    test_dir = Path("d:/TU HOC/DV_Final/data/processed")
    test_file = test_dir / "test_temp.txt"
    
    # Test 1: List Files
    logger.info("\n[1/6] Testing list_files...")
    result = file_manager.list_files(str(test_dir), "*.csv")
    assert result["success"], f"list_files failed: {result.get('error')}"
    logger.info(f"✅ Found {result['count']} CSV files")
    
    # Test 2: Create File
    logger.info("\n[2/6] Testing create_file...")
    result = file_manager.create_file(
        str(test_file),
        "This is a test file.\nLine 2.\nLine 3."
    )
    assert result["success"], f"create_file failed: {result.get('error')}"
    logger.info(f"✅ Created file: {test_file.name} ({result['size_bytes']} bytes)")
    
    # Test 3: Read File
    logger.info("\n[3/6] Testing read_file_content...")
    result = file_manager.read_file_content(str(test_file))
    assert result["success"], f"read_file_content failed: {result.get('error')}"
    assert result["lines"] == 3, f"Expected 3 lines, got {result['lines']}"
    logger.info(f"✅ Read file: {result['lines']} lines, {result['size_bytes']} bytes")
    
    # Test 4: Modify File (append)
    logger.info("\n[4/6] Testing modify_file (append)...")
    result = file_manager.modify_file(
        str(test_file),
        operation="append",
        content="Line 4 appended."
    )
    assert result["success"], f"modify_file failed: {result.get('error')}"
    logger.info(f"✅ Appended to file: {result['lines_affected']} lines affected")
    
    # Test 5: Move/Rename File
    logger.info("\n[5/6] Testing move_rename_file...")
    new_file = test_dir / "test_temp_renamed.txt"
    result = file_manager.move_rename_file(str(test_file), str(new_file))
    assert result["success"], f"move_rename_file failed: {result.get('error')}"
    logger.info(f"✅ Renamed file: {test_file.name} → {new_file.name}")
    
    # Test 6: Delete File
    logger.info("\n[6/6] Testing delete_file...")
    result = file_manager.delete_file(str(new_file))
    assert result["success"], f"delete_file failed: {result.get('error')}"
    logger.info(f"✅ Deleted file: {new_file.name} ({result['size_deleted']} bytes)")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ ALL FILE MANAGER TESTS PASSED!")
    logger.info("=" * 60)


def test_security():
    """Test security validation."""
    from app.services import file_manager
    
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Security Validation")
    logger.info("=" * 60)
    
    # Test 1: Path traversal attack
    logger.info("\n[1/4] Testing path traversal protection...")
    result = file_manager.read_file_content("../../etc/passwd")
    assert not result["success"], "Path traversal should be blocked"
    assert "Security" in result["error"], f"Expected security error, got: {result['error']}"
    logger.info("✅ Blocked path traversal attack")
    
    # Test 2: Forbidden file (.env) - test với file trong allowed directory
    logger.info("\n[2/4] Testing forbidden file pattern (.env)...")
    # Tạo file .env giả trong allowed directory để test pattern
    test_env = Path("d:/TU HOC/DV_Final/data/test.env")
    test_env.write_text("TEST_KEY=value")
    
    result = file_manager.read_file_content(str(test_env))
    assert not result["success"], ".env file should be blocked by pattern"
    assert "forbidden" in result["error"].lower(), f"Expected forbidden error, got: {result['error']}"
    
    # Cleanup
    test_env.unlink()
    logger.info("✅ Blocked access to .env pattern file")
    
    # Test 3: Outside allowed directories
    logger.info("\n[3/4] Testing access outside allowed directories...")
    result = file_manager.read_file_content("C:/Windows/System32/drivers/etc/hosts")
    assert not result["success"], "Access outside allowed dirs should be blocked"
    assert "outside allowed" in result["error"].lower(), f"Expected 'outside allowed', got: {result['error']}"
    logger.info("✅ Blocked access outside allowed directories")
    
    # Test 4: Valid file access
    logger.info("\n[4/4] Testing valid file access...")
    result = file_manager.list_files("d:/TU HOC/DV_Final/data/processed", "dim_brand.csv")
    assert result["success"], f"Valid access failed: {result.get('error')}"
    logger.info("✅ Allowed valid file access")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ ALL SECURITY TESTS PASSED!")
    logger.info("=" * 60)


def test_approval_workflow():
    """Test approval workflow manager."""
    from app.services.approval_workflow import (
        get_approval_manager,
        ActionStatus,
        RiskLevel,
    )
    
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Approval Workflow")
    logger.info("=" * 60)
    
    manager = get_approval_manager()
    session_id = "test_session_123"
    
    # Test 1: Create action
    logger.info("\n[1/5] Testing create_action...")
    action = manager.create_action(
        session_id=session_id,
        tool_name="create_file",
        arguments={"file_path": "test.csv", "content": "data"},
        preview="Test preview"
    )
    assert action.action_id, "Action ID should be generated"
    assert action.status == ActionStatus.PENDING, f"Expected PENDING, got {action.status}"
    assert action.risk_level == RiskLevel.MEDIUM, f"Expected MEDIUM risk for create_file, got {action.risk_level}"
    logger.info(f"✅ Created action: {action.action_id} (risk={action.risk_level.value})")
    
    # Test 2: Get pending actions
    logger.info("\n[2/5] Testing get_pending_actions...")
    pending = manager.get_pending_actions(session_id=session_id, status=ActionStatus.PENDING)
    assert len(pending) >= 1, f"Expected at least 1 pending action, got {len(pending)}"
    logger.info(f"✅ Found {len(pending)} pending action(s)")
    
    # Test 3: Approve action
    logger.info("\n[3/5] Testing approve_action...")
    approved = manager.approve_action(action.action_id)
    assert approved is not None, "Approval should succeed"
    assert approved.status == ActionStatus.APPROVED, f"Expected APPROVED, got {approved.status}"
    logger.info(f"✅ Approved action: {action.action_id}")
    
    # Test 4: Mark executed
    logger.info("\n[4/5] Testing mark_executed...")
    executed = manager.mark_executed(
        action.action_id,
        result={"success": True, "path": "test.csv"},
        success=True
    )
    assert executed is not None, "Mark executed should succeed"
    assert executed.status == ActionStatus.EXECUTED, f"Expected EXECUTED, got {executed.status}"
    logger.info(f"✅ Marked action as executed")
    
    # Test 5: Risk classification
    logger.info("\n[5/5] Testing risk classification...")
    test_cases = [
        ("read_file_content", RiskLevel.LOW),
        ("list_files", RiskLevel.LOW),
        ("create_file", RiskLevel.MEDIUM),
        ("modify_file", RiskLevel.HIGH),
        ("delete_file", RiskLevel.CRITICAL),
        ("move_rename_file", RiskLevel.HIGH),
    ]
    
    for tool_name, expected_risk in test_cases:
        action = manager.create_action(
            session_id=session_id,
            tool_name=tool_name,
            arguments={},
        )
        assert action.risk_level == expected_risk, (
            f"{tool_name}: Expected {expected_risk.value}, got {action.risk_level.value}"
        )
        logger.info(f"  ✅ {tool_name}: {action.risk_level.value}")
    
    # Cleanup
    manager.clear_session(session_id)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ ALL APPROVAL WORKFLOW TESTS PASSED!")
    logger.info("=" * 60)


def test_end_to_end_simulation():
    """Simulate end-to-end workflow."""
    from app.services import file_manager
    from app.services.approval_workflow import get_approval_manager, ActionStatus
    
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: End-to-End Workflow Simulation")
    logger.info("=" * 60)
    
    manager = get_approval_manager()
    session_id = "e2e_test_session"
    test_file = Path("d:/TU HOC/DV_Final/report/test_e2e_report.md")
    
    # Scenario: User yêu cầu "Tạo file báo cáo markdown"
    logger.info("\n📝 SCENARIO: User yêu cầu 'Tạo file báo cáo test_e2e_report.md'")
    
    # Step 1: AI creates pending action
    logger.info("\n[Step 1] AI tạo pending action...")
    content = "# Báo cáo Test\n\nĐây là file báo cáo test.\n\n## Kết quả\n- Test 1: OK\n- Test 2: OK"
    action = manager.create_action(
        session_id=session_id,
        tool_name="create_file",
        arguments={"file_path": str(test_file), "content": content},
        preview=content[:200]
    )
    logger.info(f"✅ Created pending action: {action.action_id} (risk={action.risk_level.value})")
    
    # Step 2: Frontend displays modal, user clicks "Approve"
    logger.info("\n[Step 2] User phê duyệt qua Frontend...")
    approved = manager.approve_action(action.action_id)
    assert approved.status == ActionStatus.APPROVED
    logger.info(f"✅ User approved action")
    
    # Step 3: Backend executes operation
    logger.info("\n[Step 3] Backend thực thi operation...")
    result = file_manager.create_file(**action.arguments)
    assert result["success"], f"Execution failed: {result.get('error')}"
    logger.info(f"✅ File created successfully: {test_file.name}")
    
    # Step 4: Mark as executed
    logger.info("\n[Step 4] Đánh dấu action đã hoàn thành...")
    executed = manager.mark_executed(action.action_id, result, success=True)
    assert executed.status == ActionStatus.EXECUTED
    logger.info(f"✅ Action marked as executed")
    
    # Step 5: Verify file exists
    logger.info("\n[Step 5] Verify file đã được tạo...")
    assert test_file.exists(), f"File should exist: {test_file}"
    read_result = file_manager.read_file_content(str(test_file))
    assert read_result["success"]
    assert "Báo cáo Test" in read_result["content"]
    logger.info(f"✅ File verified: {read_result['lines']} lines, {read_result['size_bytes']} bytes")
    
    # Cleanup
    logger.info("\n[Cleanup] Xóa file test...")
    test_file.unlink()
    manager.clear_session(session_id)
    logger.info("✅ Cleaned up")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ END-TO-END SIMULATION PASSED!")
    logger.info("=" * 60)


def main():
    """Run all tests."""
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 1 MVP - AGENTIC AI FILE MANAGEMENT SYSTEM - TEST SUITE")
    logger.info("=" * 80)
    
    try:
        test_file_manager()
        test_security()
        test_approval_workflow()
        test_end_to_end_simulation()
        
        logger.info("\n" + "=" * 80)
        logger.info("🎉 ALL TESTS PASSED! Phase 1 MVP is working correctly!")
        logger.info("=" * 80)
        
        logger.info("\n📋 SUMMARY:")
        logger.info("  ✅ File Manager Service: 6/6 operations working")
        logger.info("  ✅ Security Validation: 4/4 checks passing")
        logger.info("  ✅ Approval Workflow: 5/5 flows working")
        logger.info("  ✅ End-to-End Simulation: Complete workflow verified")
        
        logger.info("\n🚀 NEXT STEPS:")
        logger.info("  1. Start backend: python main.py")
        logger.info("  2. Test via API: POST http://localhost:8000/api/analysis/chat/stream")
        logger.info("  3. Test approval: GET http://localhost:8000/api/file-operations/pending")
        logger.info("  4. Build Frontend UI for approval modal")
        
        return 0
        
    except AssertionError as e:
        logger.error(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        logger.error(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
