from hypothesis import given, strategies as st
from bowling_alley_parser import format_player_name, parse_frame, parse_scoreboard

@given(st.text() | st.none())
def test_format_player_name_no_crash(s):
    # To-Do: Using try and except complete this function.
    try:
        result = format_player_name(s)
    except Exception as e:
        assert False, f"format_player_name crashed with: {e}"
    assert isinstance(result, str)

@given(st.text() | st.none())
def test_parse_frame_no_crash(s):
    # To-Do: Using try and except complete this function.
    try:
        result = parse_frame(s)
    except Exception as e:
        assert False, f"parse_frame crashed with: {e}"
    assert isinstance(result, tuple) and len(result) == 2

@given(st.text() | st.none())
def test_parse_scoreboard_no_crash(s):
    # To-Do: Using try and except complete this function.
    try:
        result = parse_scoreboard(s)
    except Exception as e:
        assert False, f"parse_scoreboard crashed with: {e}"
    assert isinstance(result, dict)
