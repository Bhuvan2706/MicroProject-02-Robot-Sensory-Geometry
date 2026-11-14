
import numpy as np
import pytest
from src.sensor_geometry import (calculate_relative_position,calculate_distance,normalize_vector,calculate_sensor_direction,calculate_dot_product,calculate_angle,calculate_projection,is_within_range,is_within_field_of_view,detect_object,detect_multiple_objects)

def test_calculate_relative_position():
    result = calculate_relative_position([1, 2], [4, 6])
    np.testing.assert_allclose(result, [3, 4])

def test_relative_position_negative_coordinates():
    result = calculate_relative_position([2, 3], [-1, -2])
    np.testing.assert_allclose(result, [-3, -5])

def test_calculate_distance():
    result = calculate_distance([0, 0], [3, 4])
    assert result == pytest.approx(5.0)

def test_distance_same_position():
    result = calculate_distance([2, 2], [2, 2])
    assert result == pytest.approx(0.0)

def test_normalize_vector():
    result = normalize_vector([3, 4])
    np.testing.assert_allclose(result, [0.6, 0.8])

def test_normalize_zero_vector():
    with pytest.raises(ValueError):
        normalize_vector([0, 0])

@pytest.mark.parametrize("heading, expected",[(0, [1, 0]),(90, [0, 1]),(180, [-1, 0]),(270, [0, -1]),(360, [1, 0])])

def test_calculate_sensor_direction(heading, expected):
    result = calculate_sensor_direction(heading)
    np.testing.assert_allclose(result, expected, atol=1e-10)

@pytest.mark.parametrize("heading",[np.nan, np.inf, -np.inf])

def test_invalid_sensor_heading(heading):
    with pytest.raises(ValueError):
        calculate_sensor_direction(heading)

def test_calculate_dot_product():
    result = calculate_dot_product([2, 3], [4, 5])
    assert result == pytest.approx(23.0)

def test_dot_product_perpendicular_vectors():
    result = calculate_dot_product([1, 0], [0, 1])
    assert result == pytest.approx(0.0)

@pytest.mark.parametrize(
    "vector_a, vector_b, expected",
    [
        ([1, 0], [1, 0], 0),
        ([1, 0], [0, 1], 90),
        ([1, 0], [-1, 0], 180),
        ([1, 0], [1, 1], 45)
    ]
)

def test_calculate_angle(vector_a, vector_b, expected):
    result = calculate_angle(vector_a, vector_b)
    assert result == pytest.approx(expected, abs=1e-9)

def test_angle_with_zero_vector():
    with pytest.raises(ValueError):
        calculate_angle([0, 0], [1, 0])

def test_calculate_projection():
    result = calculate_projection([3, 4], [1, 0])
    np.testing.assert_allclose(result, [3, 0])

def test_projection_non_unit_direction():
    result = calculate_projection([3, 4], [2, 0])
    np.testing.assert_allclose(result, [3, 0])

def test_projection_zero_direction():
    with pytest.raises(ValueError):
        calculate_projection([3, 4], [0, 0])

@pytest.mark.parametrize(
    "object_pos, expected",
    [
        ([5, 0], True),
        ([10, 0], True),
        ([12, 0], False),
        ([0, 0], True)
    ]
)

def test_is_within_range(object_pos, expected):
    result = is_within_range([0, 0], object_pos, 10)
    assert result == expected

def test_range_floating_point_boundary():
    result = is_within_range(
        [0, 0],
        [10 + 1e-12, 0],
        10
    )
    assert result is True

@pytest.mark.parametrize(
    "sensor_range",
    [-1, np.nan, np.inf, -np.inf]
)

def test_invalid_sensor_range(sensor_range):
    with pytest.raises(ValueError):
        is_within_range([0, 0], [1, 0], sensor_range)

@pytest.mark.parametrize(
    "object_pos, expected",
    [
        ([5, 0], True),
        ([5, 5], True),
        ([0, 5], False),
        ([-5, 0], False),
        ([5, -5], True)
    ]
)

def test_is_within_field_of_view(object_pos, expected):
    result = is_within_field_of_view(
        [0, 0],
        object_pos,
        0,
        90
    )
    assert result == expected

def test_fov_boundary_precision():
    result = is_within_field_of_view(
        [0, 0],
        [5, 5],
        0,
        90
    )
    assert result is True

def test_fov_zero_degrees():
    assert is_within_field_of_view(
        [0, 0], [5, 0], 0, 0
    ) is True

    assert is_within_field_of_view(
        [0, 0], [5, 1], 0, 0
    ) is False

def test_fov_360_degrees():
    assert is_within_field_of_view(
        [0, 0], [-5, 0], 0, 360
    ) is True

def test_object_at_robot_position():
    assert is_within_field_of_view(
        [0, 0], [0, 0], 0, 90
    ) is True

@pytest.mark.parametrize(
    "fov_angle",
    [-1, 361, np.nan, np.inf, -np.inf]
)

def test_invalid_fov_angle(fov_angle):
    with pytest.raises(ValueError):
        is_within_field_of_view(
            [0, 0], [5, 0], 0, fov_angle
        )

@pytest.mark.parametrize(
    "heading",
    [np.nan, np.inf, -np.inf]
)

def test_invalid_heading_in_fov(heading):
    with pytest.raises(ValueError):
        is_within_field_of_view(
            [0, 0], [5, 0], heading, 90
        )

def test_detect_object_inside_sensor():
    result = detect_object(
        [0, 0], [5, 5], 0, 10, 90
    )

    assert result["detected"] is True
    assert result["within_range"] is True
    assert result["within_fov"] is True
    assert result["distance"] == pytest.approx(np.sqrt(50))
    assert result["angle"] == pytest.approx(45.0)

def test_detect_object_outside_range():
    result = detect_object(
        [0, 0], [12, 0], 0, 10, 90
    )

    assert result["detected"] is False
    assert result["within_range"] is False
    assert result["within_fov"] is True

def test_detect_object_outside_fov():
    result = detect_object(
        [0, 0], [0, 5], 0, 10, 90
    )

    assert result["detected"] is False
    assert result["within_range"] is True
    assert result["within_fov"] is False

def test_detect_object_same_position():
    result = detect_object(
        [0, 0], [0, 0], 0, 10, 90
    )

    assert result["detected"] is True
    assert result["distance"] == pytest.approx(0.0)
    assert result["angle"] == pytest.approx(0.0)

def test_detect_multiple_objects():
    objects_pos = [
        [5, 0],
        [5, 5],
        [0, 5],
        [12, 0],
        [-3, 0]
    ]

    results = detect_multiple_objects(
        [0, 0],
        objects_pos,
        0,
        10,
        90
    )

    assert len(results) == 5

    expected = [True, True, False, False, False]

    for index, result in enumerate(results):
        assert result["detected"] == expected[index]
        assert result["object_index"] == index + 1

        np.testing.assert_allclose(
            result["position"],
            objects_pos[index]
        )

def test_detect_multiple_objects_empty():
    results = detect_multiple_objects(
        [0, 0],
        [],
        0,
        10,
        90
    )

    assert results == []
