from src.tick_app.utils import format_duration

def test_format_duration():
    assert format_duration(3661) == "1h 1m 1s"
    assert format_duration(60) == "0h 1m 0s"
    assert format_duration(0) == "0h 0m 0s"
