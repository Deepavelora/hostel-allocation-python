from app.allocate import form_groups
from app.allocate import (
    _repair_lonely,
    allocate,
    is_viable_occupancy,
    mutual_pairs,
    one_way_requests,
    rank_students,
    room_score,
)


def student(student_id, name, merit=80, year=1, wants=None):
    return {
        "id": student_id,
        "name": name,
        "merit": merit,
        "year": year,
        "wants": wants or [],
    }


def test_merit_key_uses_merit_then_year_then_id():
    students = [
        student(3, "C", merit=80, year=2),
        student(1, "A", merit=90, year=1),
        student(2, "B", merit=90, year=1),
        student(4, "D", merit=80, year=3),
    ]

    ranked = rank_students(students)

    assert [s["id"] for s in ranked] == [1, 2, 4, 3]
    assert [s["rank"] for s in ranked] == [1, 2, 3, 4]


def test_mutual_pairs_only_returns_mutual_requests():
    students = [
        student(1, "A", wants=[2]),
        student(2, "B", wants=[1]),
        student(3, "C", wants=[1]),
    ]

    assert mutual_pairs(students) == [(1, 2)]


def test_mutual_pairs_ignores_self_request():
    students = [
        student(1, "A", wants=[1]),
    ]

    assert mutual_pairs(students) == []


def test_one_way_requests_are_reported():
    students = [
        student(1, "Ishita", wants=[2]),
        student(2, "Janvi", wants=[3]),
        student(3, "Kabir", wants=[]),
    ]

    result = one_way_requests(students)

    assert result == [
        {
            "student": 1,
            "name": "Ishita",
            "wanted": 2,
            "wanted_name": "Janvi",
            "reason": "not_mutual",
        },
        {
            "student": 2,
            "name": "Janvi",
            "wanted": 3,
            "wanted_name": "Kabir",
            "reason": "not_mutual",
        },
    ]


def test_is_viable_occupancy():
    assert is_viable_occupancy(4, 1) is False
    assert is_viable_occupancy(1, 1) is True
    assert is_viable_occupancy(2, 1) is True
    assert is_viable_occupancy(4, 0) is True

def test_form_groups_respects_maximum_group_size():
    students = [
        student(1, "A", merit=95, wants=[2, 3]),
        student(2, "B", merit=90, wants=[1, 3]),
        student(3, "C", merit=85, wants=[1, 2]),
        student(4, "D", merit=80, wants=[1, 3]),
        student(5, "E", merit=70, wants=[1, 4]),
    ]

    ranked = rank_students(students)

    groups, bumped = form_groups(ranked, max_size=4)

    assert all(len(group) <= 4 for group in groups)

def test_room_score_prefers_requested_room_type():
    leader = {
        "id": 1,
        "name": "A",
        "merit": 90,
        "year": 2,
        "room_type": "double",
        "floor_pref": 2,
    }

    double_room = {
        "id": 1,
        "room_type": "double",
        "floor": 5,
        "capacity": 2,
    }

    single_room = {
        "id": 2,
        "room_type": "single",
        "floor": 2,
        "capacity": 1,
    }

    double_score = room_score(double_room, 1, leader)
    single_score = room_score(single_room, 1, leader)

    assert double_score > single_score

def test_repair_lonely_moves_student_to_smaller_room():
    state = [
        {
            "id": 1,
            "code": "Q1",
            "capacity": 4,
            "occupants": [1],
        },
        {
            "id": 2,
            "code": "D1",
            "capacity": 2,
            "occupants": [],
        },
    ]

    moved, stranded = _repair_lonely(state)

    assert moved == [
        {
            "student": 1,
            "from": "Q1",
            "to": "D1",
            "reason": "would have been alone in a 4-bed room",
        }
    ]

    assert stranded == []

    assert state[0]["occupants"] == []
    assert state[1]["occupants"] == [1]

def test_repair_lonely_brings_someone_into_big_room():
    state = [
        {
            "id": 1,
            "code": "Q1",
            "capacity": 4,
            "occupants": [1],
        },
        {
            "id": 2,
            "code": "D1",
            "capacity": 2,
            "occupants": [2, 3],
        },
    ]

    # Student 1 is alone in the quad.
    # The double room is full, so student 2 or 3 must be moved into the quad.
    moved, stranded = _repair_lonely(
        state,
        pos={1: 1, 2: 2, 3: 3},
    )

    assert stranded == []

    assert moved[0]["student"] in [2, 3]
    assert moved[0]["from"] == "D1"
    assert moved[0]["to"] == "Q1"
    assert "moved in for company" in moved[0]["reason"]

    assert state[0]["occupants"] == [1, moved[0]["student"]]
    assert len(state[1]["occupants"])

def test_allocate_is_deterministic():
    students = [
        student(1, "A", merit=90, wants=[2]),
        student(2, "B", merit=85, wants=[1]),
        student(3, "C", merit=80),
    ]

    rooms = [
        {"id": 1, "code": "D1", "room_type": "double", "floor": 1},
        {"id": 2, "code": "S1", "room_type": "single", "floor": 1},
    ]

    result1 = allocate(students, rooms)
    result2 = allocate(students, rooms)

    assert result1 == result2
