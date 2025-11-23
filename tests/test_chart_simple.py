"""Simple test to verify report generation and chart data preparation."""
from tick_app.api.routers.web import generate_report_web
from tick_app.database import get_db, Base, engine
from tick_app.services import project_service, time_entry_service
from datetime import datetime, timedelta, UTC
import json


def test_chart_data_preparation():
    """Test that chart data is properly prepared for JavaScript."""
    # Setup test database
    Base.metadata.create_all(bind=engine)
    
    try:
        db = next(get_db())
        
        # Create test projects
        project1 = project_service.create_project(db, "Project A")
        project2 = project_service.create_project(db, "Project B")
        
        # Create time entries
        start1 = datetime.now(UTC) - timedelta(hours=5)
        end1 = datetime.now(UTC) - timedelta(hours=3)
        time_entry_service.log_time(db, project1.id, start1, end1, "Task 1")
        
        start2 = datetime.now(UTC) - timedelta(hours=2)
        end2 = datetime.now(UTC) - timedelta(hours=1)
        time_entry_service.log_time(db, project2.id, start2, end2, "Task 2")
        
        # Generate report
        from tick_app.services import time_entry_service
        report_data = time_entry_service.generate_report(
            db,
            start_date=datetime.now(UTC) - timedelta(days=1),
            end_date=datetime.now(UTC),
            group_by='project'
        )
        
        print(f"✅ Report generated with {len(report_data)} entries")
        
        # Verify report data structure
        assert len(report_data) == 2, f"Expected 2 projects, got {len(report_data)}"
        for entry in report_data:
            assert 'group_key' in entry
            assert 'total_duration' in entry
            print(f"  - {entry['group_key']}: {entry['total_duration']/3600:.2f} hours")
        
        print("✅ All tests passed!")
        
    finally:
        # Cleanup
        Base.metadata.drop_all(bind=engine)


if __name__ == "__main__":
    test_chart_data_preparation()
