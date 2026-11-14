
import numpy as np
from src.sensor_geometry import detect_multiple_objects
from src.visualization import plot_sensor_detection


def get_float_input(prompt):
    while True:
        try:
            value = float(input(prompt))

            if not np.isfinite(value):
                print("Please enter a finite number.")
                continue

            return value

        except ValueError:
            print("Invalid input. Please enter a valid number.")


def get_position_input(name):
    print(f"\nEnter {name} coordinates:")

    x = get_float_input("X coordinate: ")
    y = get_float_input("Y coordinate: ")

    return [x, y]


def get_sensor_input():
    while True:
        sensor_range = get_float_input(
            "\nEnter sensor detection range (> 0): "
        )

        if sensor_range > 0:
            return sensor_range

        print("Sensor range must be greater than 0.")


def get_fov_angle():
    while True:
        fov_angle = get_float_input(
            "Enter field of view angle (0-360 degrees): "
        )

        if 0 <= fov_angle <= 360:
            return fov_angle

        print("FOV angle must be between 0 and 360 degrees.")


def get_object_count():
    while True:
        try:
            count = int(input("\nEnter number of objects: "))

            if count >= 0:
                return count

            print("Number of objects cannot be negative.")

        except ValueError:
            print("Invalid input. Please enter a valid whole number.")


def get_objects():
    objects_pos = []

    count = get_object_count()

    for index in range(count):
        position = get_position_input(f"Object {index + 1}")
        objects_pos.append(position)

    return objects_pos


def main():
    print("=" * 55)
    print("        ROBOT SENSOR GEOMETRY SIMULATOR")
    print("=" * 55)

    robot_pos = get_position_input("Robot")

    print("\n--- Sensor Configuration ---")

    heading_angle = get_float_input(
        "Enter sensor heading angle (degrees): "
    )

    sensor_range = get_sensor_input()
    fov_angle = get_fov_angle()

    print("\n--- Object Configuration ---")

    objects_pos = get_objects()

    detections = detect_multiple_objects(
        robot_pos,
        objects_pos,
        heading_angle,
        sensor_range,
        fov_angle
    )

    print("\n" + "=" * 55)
    print("                 DETECTION RESULTS")
    print("=" * 55)

    for result in detections:
        status = (
            "DETECTED"
            if result["detected"]
            else "NOT DETECTED"
        )

        print(f"\nObject {result['object_index']}")
        print(f"Position: {result['position']}")
        print(f"Distance: {result['distance']:.2f}")
        print(f"Angle: {result['angle']:.2f} degrees")
        print(f"Within Range: {result['within_range']}")
        print(f"Within FOV: {result['within_fov']}")
        print(f"Status: {status}")

    detected_count = sum(
        result["detected"] for result in detections
    )

    undetected_count = len(detections) - detected_count

    print("\n" + "=" * 55)
    print("                 DETECTION SUMMARY")
    print("=" * 55)

    print(f"Robot Position: {robot_pos}")
    print(f"Sensor Heading: {heading_angle} degrees")
    print(f"Sensor Range: {sensor_range}")
    print(f"Field of View: {fov_angle} degrees")
    print(f"Total Objects: {len(detections)}")
    print(f"Detected Objects: {detected_count}")
    print(f"Undetected Objects: {undetected_count}")

    plot_sensor_detection(
        robot_pos,
        objects_pos,
        heading_angle,
        sensor_range,
        fov_angle,
        detections,
        save=True
    )


if __name__ == "__main__":
    main()
