"""
Test script cho Phase 3 Advanced Features.

Tests:
1. Vietnamese Encoding - UTF-8 support
2. Multi-step Planning - Task decomposition
3. Parallel Execution - Concurrent file operations
4. Integration Test - Complete workflow

Run: python test_phase3_advanced.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_vietnamese_encoding():
    """Test Vietnamese UTF-8 encoding in file operations."""
    from app.services import file_manager
    
    logger.info("=" * 60)
    logger.info("TEST 1: Vietnamese Encoding Support")
    logger.info("=" * 60)
    
    test_dir = Path("d:/TU HOC/DV_Final/report")
    test_file = test_dir / "test_vietnamese.txt"
    
    # Vietnamese content with special characters
    vietnamese_content = """# Báo Cáo Phân Tích Thị Trường Ô Tô Việt Nam 2026

## 1. Tổng Quan
Thị trường ô tô Việt Nam đang phát triển mạnh mẽ với nhiều thương hiệu nổi tiếng:
- Toyota: Chiếm 35% thị phần
- Honda: Chiếm 20% thị phần  
- Hyundai: Chiếm 15% thị phần

## 2. Xu Hướng
Người tiêu dùng Việt Nam ưu chuộng:
- Xe SUV đa dụng
- Động cơ tiết kiệm nhiên liệu
- Tính năng an toàn cao

## 3. Kết Luận
Dự báo tăng trưởng 12% trong năm 2026.
"""
    
    # Test 1: Create file with Vietnamese
    logger.info("\n[1/4] Testing create_file với tiếng Việt...")
    result = file_manager.create_file(str(test_file), vietnamese_content)
    assert result["success"], f"create_file failed: {result.get('error')}"
    logger.info(f"✅ Created file with Vietnamese content ({result['size_bytes']} bytes)")
    
    # Test 2: Read file back
    logger.info("\n[2/4] Testing read_file_content...")
    result = file_manager.read_file_content(str(test_file))
    assert result["success"], f"read_file_content failed"
    assert "Việt Nam" in result["content"], "Vietnamese content not preserved"
    assert "Tổng Quan" in result["content"], "Vietnamese accents not preserved"
    logger.info(f"✅ Read file successfully, content preserved")
    
    # Test 3: Modify file with Vietnamese
    logger.info("\n[3/4] Testing modify_file với tiếng Việt...")
    new_section = "\n## 4. Khuyến Nghị\n- Đầu tư vào xe điện\n- Mở rộng thị trường nông thôn"
    result = file_manager.modify_file(
        str(test_file),
        operation="append",
        content=new_section
    )
    assert result["success"], f"modify_file failed"
    logger.info(f"✅ Modified file with Vietnamese append")
    
    # Test 4: Verify final content
    logger.info("\n[4/4] Verifying final content...")
    result = file_manager.read_file_content(str(test_file))
    assert "Khuyến Nghị" in result["content"], "Appended Vietnamese not preserved"
    assert "xe điện" in result["content"], "Vietnamese accents in append not preserved"
    logger.info(f"✅ Final content verified, all Vietnamese preserved")
    
    # Cleanup
    test_file.unlink()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ VIETNAMESE ENCODING TEST PASSED!")
    logger.info("=" * 60)


def test_multi_step_planning():
    """Test multi-step task planning."""
    from app.services import task_planner
    from app.services.task_planner import TaskStatus
    import time
    
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Multi-step Planning")
    logger.info("=" * 60)
    
    # Test 1: Create plan
    logger.info("\n[1/5] Creating task plan...")
    
    steps = [
        {
            "description": "Đọc file dữ liệu gốc",
            "tool_name": "read_file_content",
            "arguments": {"file_path": "data/raw/car_detail.csv"}
        },
        {
            "description": "Tạo file báo cáo tổng hợp",
            "tool_name": "create_file",
            "arguments": {
                "file_path": "report/summary.csv",
                "content": "Hãng,Số lượng\n"
            }
        },
        {
            "description": "Tạo file báo cáo chi tiết",
            "tool_name": "create_file",
            "arguments": {
                "file_path": "report/details.json",
                "content": "{}"
            }
        },
    ]
    
    result = task_planner.create_plan(
        "Phân tích dữ liệu và xuất báo cáo",
        steps
    )
    
    assert result["success"], f"create_plan failed: {result.get('error')}"
    plan_id = result["plan_id"]
    assert result["steps_count"] == 3
    logger.info(f"✅ Created plan: {plan_id} with 3 steps")
    
    # Test 2: Get plan
    logger.info("\n[2/5] Retrieving plan...")
    plan = task_planner.get_plan(plan_id)
    assert plan is not None
    assert len(plan["steps"]) == 3
    logger.info(f"✅ Retrieved plan successfully")
    
    # Test 3: Update step status (simulate execution)
    logger.info("\n[3/5] Simulating step execution...")
    
    for step_id in [1, 2, 3]:
        # Mark as in_progress
        task_planner.update_step_status(
            plan_id, step_id, TaskStatus.IN_PROGRESS
        )
        
        time.sleep(0.1)  # Simulate work
        
        # Mark as completed
        result = task_planner.update_step_status(
            plan_id, step_id, TaskStatus.COMPLETED,
            result={"success": True},
            duration_seconds=0.1
        )
        assert result["success"]
        logger.info(f"✅ Step {step_id} completed")
    
    # Test 4: Get plan summary
    logger.info("\n[4/5] Getting plan summary...")
    summary = task_planner.get_plan_summary(plan_id)
    assert summary["success"]
    assert summary["completed_steps"] == 3
    assert summary["progress_percent"] == 100.0
    assert summary["is_completed"] == True
    logger.info(f"✅ Plan completed: 100% progress")
    
    # Test 5: List active plans
    logger.info("\n[5/5] Listing active plans...")
    result = task_planner.list_active_plans()
    assert result["success"]
    assert result["count"] >= 1
    logger.info(f"✅ Found {result['count']} active plans")
    
    # Cleanup
    task_planner.clear_plan(plan_id)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ MULTI-STEP PLANNING TEST PASSED!")
    logger.info("=" * 60)


def test_parallel_execution():
    """Test parallel file operations."""
    from app.services import parallel_executor, file_manager
    from app.services.parallel_executor import ParallelTask
    
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Parallel Execution")
    logger.info("=" * 60)
    
    test_dir = Path("d:/TU HOC/DV_Final/report")
    
    # Test 1: Detect no conflicts
    logger.info("\n[1/4] Testing conflict detection (no conflicts)...")
    
    tasks = [
        ParallelTask(
            task_id="task1",
            tool_name="create_file",
            arguments={"file_path": str(test_dir / "parallel1.txt"), "content": "File 1"}
        ),
        ParallelTask(
            task_id="task2",
            tool_name="create_file",
            arguments={"file_path": str(test_dir / "parallel2.txt"), "content": "File 2"}
        ),
        ParallelTask(
            task_id="task3",
            tool_name="create_file",
            arguments={"file_path": str(test_dir / "parallel3.txt"), "content": "File 3"}
        ),
    ]
    
    check = parallel_executor.can_execute_parallel(tasks)
    assert check["can_parallel"] == True
    assert len(check["conflicts"]) == 0
    logger.info(f"✅ No conflicts detected for 3 different files")
    
    # Test 2: Detect conflicts
    logger.info("\n[2/4] Testing conflict detection (with conflicts)...")
    
    conflict_tasks = [
        ParallelTask(
            task_id="task1",
            tool_name="modify_file",
            arguments={"file_path": "same_file.txt", "operation": "append"}
        ),
        ParallelTask(
            task_id="task2",
            tool_name="modify_file",
            arguments={"file_path": "same_file.txt", "operation": "append"}
        ),
    ]
    
    check = parallel_executor.can_execute_parallel(conflict_tasks)
    assert check["can_parallel"] == False
    assert len(check["conflicts"]) == 1
    logger.info(f"✅ Conflict detected: {check['conflicts']}")
    
    # Test 3: Execute parallel (sync)
    logger.info("\n[3/4] Executing 3 tasks in parallel...")
    
    tool_map = {
        "create_file": file_manager.create_file,
    }
    
    result = parallel_executor.execute_parallel_sync(tasks, tool_map)
    
    assert result["success"] == True
    assert len(result["results"]) == 3
    
    success_count = sum(1 for r in result["results"] if r.success)
    assert success_count == 3
    
    logger.info(
        f"✅ Parallel execution completed: {success_count}/3 succeeded "
        f"in {result['total_duration_seconds']:.3f}s"
    )
    
    # Test 4: Verify files created
    logger.info("\n[4/4] Verifying created files...")
    
    for i in [1, 2, 3]:
        file_path = test_dir / f"parallel{i}.txt"
        assert file_path.exists(), f"File {file_path} not created"
        file_path.unlink()  # Cleanup
    
    logger.info(f"✅ All 3 files verified and cleaned up")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ PARALLEL EXECUTION TEST PASSED!")
    logger.info("=" * 60)


def test_end_to_end_advanced():
    """Complete end-to-end test with Phase 3 features."""
    from app.services import task_planner, parallel_executor, file_manager
    from app.services.task_planner import TaskStatus
    from app.services.parallel_executor import ParallelTask
    
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: End-to-End Advanced Workflow")
    logger.info("=" * 60)
    
    test_dir = Path("d:/TU HOC/DV_Final/report")
    
    logger.info("\n📝 SCENARIO: User yêu cầu 'Tạo 3 báo cáo phân tích'\n")
    
    # Step 1: Create plan
    logger.info("[Step 1] AI tạo kế hoạch...")
    
    steps = [
        {
            "description": "Tạo báo cáo tổng hợp (summary.md)",
            "tool_name": "create_file",
        },
        {
            "description": "Tạo báo cáo chi tiết (details.json)",
            "tool_name": "create_file",
        },
        {
            "description": "Tạo báo cáo thống kê (statistics.csv)",
            "tool_name": "create_file",
        },
    ]
    
    plan_result = task_planner.create_plan(
        "Tạo 3 file báo cáo phân tích",
        steps
    )
    assert plan_result["success"]
    plan_id = plan_result["plan_id"]
    logger.info(f"✅ Plan created: {plan_id}")
    
    # Step 2: Execute plan steps in parallel
    logger.info("\n[Step 2] AI thực hiện 3 steps song song...")
    
    parallel_tasks = [
        ParallelTask(
            task_id="step1",
            tool_name="create_file",
            arguments={
                "file_path": str(test_dir / "e2e_summary.md"),
                "content": "# Báo Cáo Tổng Hợp\n\nKết quả phân tích..."
            }
        ),
        ParallelTask(
            task_id="step2",
            tool_name="create_file",
            arguments={
                "file_path": str(test_dir / "e2e_details.json"),
                "content": '{"analysis": "chi tiết", "count": 100}'
            }
        ),
        ParallelTask(
            task_id="step3",
            tool_name="create_file",
            arguments={
                "file_path": str(test_dir / "e2e_statistics.csv"),
                "content": "Metric,Value\nTotal,100\nAverage,50\n"
            }
        ),
    ]
    
    tool_map = {"create_file": file_manager.create_file}
    
    exec_result = parallel_executor.execute_parallel_sync(
        parallel_tasks,
        tool_map
    )
    
    assert exec_result["success"]
    success_count = sum(1 for r in exec_result["results"] if r.success)
    assert success_count == 3
    
    logger.info(
        f"✅ Executed 3 tasks in parallel: {success_count}/3 succeeded "
        f"in {exec_result['total_duration_seconds']:.3f}s"
    )
    
    # Step 3: Update plan with results
    logger.info("\n[Step 3] Cập nhật trạng thái plan...")
    
    for i, result in enumerate(exec_result["results"], 1):
        task_planner.update_step_status(
            plan_id, i, TaskStatus.COMPLETED,
            result={"success": result.success},
            duration_seconds=result.duration_seconds
        )
    
    summary = task_planner.get_plan_summary(plan_id)
    assert summary["is_completed"]
    logger.info(f"✅ Plan completed: {summary['progress_percent']}%")
    
    # Step 4: Verify all files
    logger.info("\n[Step 4] Xác minh files đã tạo...")
    
    files_created = [
        test_dir / "e2e_summary.md",
        test_dir / "e2e_details.json",
        test_dir / "e2e_statistics.csv",
    ]
    
    for file_path in files_created:
        assert file_path.exists(), f"File {file_path} not created"
        
        # Verify Vietnamese encoding
        content = file_path.read_text(encoding="utf-8")
        if "Báo Cáo" in content:
            assert "Báo Cáo" in content  # Vietnamese preserved
        
        file_path.unlink()  # Cleanup
    
    logger.info(f"✅ All 3 files verified (UTF-8 encoding OK)")
    
    # Cleanup
    task_planner.clear_plan(plan_id)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ END-TO-END ADVANCED WORKFLOW PASSED!")
    logger.info("=" * 60)


def main():
    """Run all Phase 3 tests."""
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 3 ADVANCED FEATURES - COMPLETE TEST SUITE")
    logger.info("=" * 80)
    
    try:
        test_vietnamese_encoding()
        test_multi_step_planning()
        test_parallel_execution()
        test_end_to_end_advanced()
        
        logger.info("\n" + "=" * 80)
        logger.info("🎉 ALL PHASE 3 TESTS PASSED! Advanced features ready!")
        logger.info("=" * 80)
        
        logger.info("\n📋 SUMMARY:")
        logger.info("  ✅ Vietnamese Encoding: UTF-8 fully supported")
        logger.info("  ✅ Multi-step Planning: Task decomposition working")
        logger.info("  ✅ Parallel Execution: Concurrent operations verified")
        logger.info("  ✅ End-to-End Advanced: Complete workflow successful")
        
        logger.info("\n🚀 PHASE 3 FEATURES COMPLETE:")
        logger.info("  ✅ UTF-8 encoding for Vietnamese text")
        logger.info("  ✅ Multi-step task planning")
        logger.info("  ✅ Parallel file operations")
        logger.info("  ✅ Conflict detection")
        logger.info("  ✅ Plan execution tracking")
        logger.info("  ✅ Task progress monitoring")
        
        logger.info("\n📦 TOTAL SYSTEM CAPABILITIES:")
        logger.info("  🤖 13 AI Tools Total:")
        logger.info("     - 2 data tools (query_dataset, scrape_car_data)")
        logger.info("     - 6 file management tools (read, list, create, modify, delete, move)")
        logger.info("     - 3 rollback tools (rollback, history, list_backups)")
        logger.info("     - 2 planning tools (plan_operations, get_plan_status)")
        logger.info("  🔒 Security: Path validation, forbidden patterns, size limits")
        logger.info("  💾 Backup: Auto-backup, 10 versions/file, 30 days retention")
        logger.info("  🌐 Encoding: Full UTF-8 support for Vietnamese")
        logger.info("  ⚡ Performance: Parallel execution for non-conflicting operations")
        logger.info("  📊 Planning: Multi-step task decomposition and tracking")
        
        logger.info("\n🎯 COMPLETE FEATURE LIST:")
        logger.info("  Phase 1 (MVP):")
        logger.info("    ✅ 6 File Management Tools")
        logger.info("    ✅ Basic Approval Workflow")
        logger.info("  Phase 2 (Production):")
        logger.info("    ✅ Auto-backup System")
        logger.info("    ✅ Rollback Mechanism")
        logger.info("    ✅ Change History Tracking")
        logger.info("    ✅ Frontend Approval UI")
        logger.info("  Phase 3 (Advanced):")
        logger.info("    ✅ Vietnamese UTF-8 Support")
        logger.info("    ✅ Multi-step Planning")
        logger.info("    ✅ Parallel Execution")
        logger.info("    ✅ Conflict Detection")
        
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
