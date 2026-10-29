import pytest
from bowling_alley import lane_cost, frame_score, lane_assignment

#Example test cases:
def test_weekday_booking():
    assert lane_cost("weekday", 2, 4, 2, False) == 900

def test_open_frame():
    assert frame_score(3, 4, []) == 7

#lane cost tests
def test_weekend_booking_league_member():
    assert lane_cost("weekend", 3, 6, 4, True) == 1840

def test_one_game_weekday():
    assert lane_cost("weekday", 1, 2, 0, False) == 400

def test_weekend_group_with_shoes():
    assert lane_cost("weekend", 2, 5, 5, False) == 1650

def test_unknown_day_type_raises():
    with pytest.raises(ValueError, match="unknown day type"):
        lane_cost("holiday", 1, 2, 0, False)

def test_zero_games_raises():
    with pytest.raises(ValueError, match="invalid booking"):
        lane_cost("weekday", 0, 2, 0, False)

def test_too_many_players_raises():
    with pytest.raises(ValueError, match="invalid booking"):
        lane_cost("weekday", 1, 7, 0, False)

#frame score tests
def test_strike_frame():
    assert frame_score(10, 0, [7, 2]) == 19

def test_spare_frame():
    assert frame_score(7, 3, [5]) == 15

def test_gutter_frame():
    assert frame_score(0, 0, []) == 0

def test_frame_over_ten_raises():
    with pytest.raises(ValueError, match="invalid frame"):
        frame_score(5, 6, [])

#lane assignment tests
def test_standard_lane():
    assert lane_assignment(4, False, 2) == "standard lane"

def test_bumper_lane_for_kids():
    assert lane_assignment(3, True, 2) == "bumper lane"

def test_no_free_lane():
    assert lane_assignment(4, False, 0) == "wait"

def test_big_group_two_lanes():
    assert lane_assignment(7, False, 3) == "two lanes"
