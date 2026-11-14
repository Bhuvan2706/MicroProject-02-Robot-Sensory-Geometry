
import numpy as np


def calculate_relative_position(robot_pos, object_pos):
    robot_pos = np.array(robot_pos, dtype=float)
    object_pos = np.array(object_pos, dtype=float)

    return object_pos - robot_pos


def calculate_distance(robot_pos, object_pos):
    relative_position = calculate_relative_position(
        robot_pos, object_pos
    )

    distance = float(np.linalg.norm(relative_position))

    return distance


def normalize_vector(vector):
    vector = np.array(vector, dtype=float)
    norm = np.linalg.norm(vector)

    if norm == 0:
        raise ValueError("Cannot normalize a zero vector.")

    return vector / norm


def calculate_sensor_direction(heading_angle):
    if not np.isfinite(heading_angle):
        raise ValueError("Heading angle must be finite.")

    angle_rad = np.deg2rad(heading_angle)

    direction_vector = np.array([
        np.cos(angle_rad),
        np.sin(angle_rad)
    ])

    return direction_vector


def calculate_dot_product(vector_a, vector_b):
    vector_a = np.array(vector_a, dtype=float)
    vector_b = np.array(vector_b, dtype=float)

    return float(np.dot(vector_a, vector_b))


def calculate_angle(vector_a, vector_b):
    unit_a = normalize_vector(vector_a)
    unit_b = normalize_vector(vector_b)

    dot_product = calculate_dot_product(unit_a, unit_b)
    dot_product = np.clip(dot_product, -1.0, 1.0)

    angle_rad = np.arccos(dot_product)

    return float(np.rad2deg(angle_rad))


def calculate_projection(vector, direction):
    vector = np.array(vector, dtype=float)
    direction = normalize_vector(direction)

    projection_length = calculate_dot_product(
        vector, direction
    )

    projection_vector = projection_length * direction

    return projection_vector


def is_within_range(robot_pos, object_pos, sensor_range):
    if not np.isfinite(sensor_range) or sensor_range < 0:
        raise ValueError(
            "Sensor range must be finite and non-negative."
        )

    distance = calculate_distance(robot_pos, object_pos)

    return bool(
        distance <= sensor_range
        or np.isclose(
            distance,
            sensor_range,
            rtol=0,
            atol=1e-9
        )
    )


def is_within_field_of_view(
    robot_pos,
    object_pos,
    heading_angle,
    fov_angle
):
    if not np.isfinite(heading_angle):
        raise ValueError("Heading angle must be finite.")

    if not np.isfinite(fov_angle) or not (0 <= fov_angle <= 360):
        raise ValueError(
            "Field of view angle must be between 0 and 360 degrees."
        )

    relative_position = calculate_relative_position(
        robot_pos, object_pos
    )

    if np.linalg.norm(relative_position) == 0:
        return True

    sensor_direction = calculate_sensor_direction(
        heading_angle
    )

    angle_to_object = calculate_angle(
        sensor_direction,
        relative_position
    )

    half_fov = fov_angle / 2

    return bool(
        angle_to_object <= half_fov
        or np.isclose(
            angle_to_object,
            half_fov,
            rtol=0,
            atol=1e-9
        )
    )


def detect_object(
    robot_pos,
    object_pos,
    heading_angle,
    sensor_range,
    fov_angle
):
    within_range = is_within_range(
        robot_pos,
        object_pos,
        sensor_range
    )

    within_fov = is_within_field_of_view(
        robot_pos,
        object_pos,
        heading_angle,
        fov_angle
    )

    distance = calculate_distance(
        robot_pos,
        object_pos
    )

    relative_position = calculate_relative_position(
        robot_pos,
        object_pos
    )

    sensor_direction = calculate_sensor_direction(
        heading_angle
    )

    if distance == 0:
        angle = 0.0
    else:
        angle = calculate_angle(
            sensor_direction,
            relative_position
        )

    return {
        "detected": bool(within_range and within_fov),
        "distance": distance,
        "angle": angle,
        "within_range": bool(within_range),
        "within_fov": bool(within_fov)
    }


def detect_multiple_objects(
    robot_pos,
    objects_pos,
    heading_angle,
    sensor_range,
    fov_angle
):
    detections = []

    for index, object_position in enumerate(objects_pos):
        detection_result = detect_object(
            robot_pos,
            object_position,
            heading_angle,
            sensor_range,
            fov_angle
        )

        detection_result["object_index"] = index + 1

        detection_result["position"] = np.array(
            object_position,
            dtype=float
        )

        detections.append(detection_result)

    return detections
