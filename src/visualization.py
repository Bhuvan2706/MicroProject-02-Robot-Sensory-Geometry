
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle
from pathlib import Path


def plot_sensor_detection(
    robot_pos,
    objects_pos,
    heading_angle,
    sensor_range,
    fov_angle,
    detections,
    save=True
):
    robot_pos = np.asarray(robot_pos, dtype=float)
    objects_pos = np.asarray(objects_pos, dtype=float).reshape(-1, 2)

    fig, ax = plt.subplots(figsize=(10, 8))

    sensor_cone = Wedge(
        center=robot_pos,
        r=sensor_range,
        theta1=heading_angle - fov_angle / 2,
        theta2=heading_angle + fov_angle / 2,
        facecolor="royalblue",
        alpha=0.18,
        edgecolor="blue",
        linewidth=2
    )

    ax.add_patch(sensor_cone)

    detection_boundary = Circle(
        robot_pos,
        radius=sensor_range,
        fill=False,
        edgecolor="gray",
        linestyle="--",
        linewidth=1.5,
        alpha=0.6
    )

    ax.add_patch(detection_boundary)

    ax.scatter(
        robot_pos[0],
        robot_pos[1],
        color="blue",
        s=180,
        marker="o",
        label="Robot",
        zorder=5
    )

    heading_rad = np.deg2rad(heading_angle)

    direction = np.array([
        np.cos(heading_rad),
        np.sin(heading_rad)
    ])

    arrow_length = sensor_range * 0.6

    ax.arrow(
        robot_pos[0],
        robot_pos[1],
        direction[0] * arrow_length,
        direction[1] * arrow_length,
        head_width=max(sensor_range * 0.05, 0.1),
        head_length=max(sensor_range * 0.08, 0.15),
        fc="blue",
        ec="blue",
        linewidth=2,
        length_includes_head=True,
        zorder=6
    )

    for object_pos, detection in zip(objects_pos, detections):
        detected = detection["detected"]

        color = "green" if detected else "red"

        ax.scatter(
            object_pos[0],
            object_pos[1],
            color=color,
            s=110,
            marker="o" if detected else "x",
            linewidths=2,
            zorder=7
        )

        ax.annotate(
            f"Object {detection['object_index']}\n"
            f"D={detection['distance']:.2f}\n"
            f"A={detection['angle']:.1f}°",
            xy=object_pos,
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=9
        )

    ax.scatter([], [], color="green", label="Detected Object")
    ax.scatter([], [], color="red", marker="x", label="Undetected Object")

    detected_count = sum(
        detection["detected"] for detection in detections
    )

    ax.set_title(
        "2D Robot Sensor Geometry Simulation\n"
        f"Heading: {heading_angle}° | "
        f"FOV: {fov_angle}° | "
        f"Range: {sensor_range} | "
        f"Detected: {detected_count}/{len(detections)}",
        fontsize=13
    )

    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")

    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="best")

    all_x = np.concatenate(([robot_pos[0]], objects_pos[:, 0]))
    all_y = np.concatenate(([robot_pos[1]], objects_pos[:, 1]))

    padding = max(sensor_range * 1.2, 1.0)

    ax.set_xlim(
        min(all_x.min(), robot_pos[0] - padding),
        max(all_x.max(), robot_pos[0] + padding)
    )

    ax.set_ylim(
        min(all_y.min(), robot_pos[1] - padding),
        max(all_y.max(), robot_pos[1] + padding)
    )

    plt.tight_layout()

    if save:
        results_dir = Path(__file__).resolve().parent.parent / "results"
        results_dir.mkdir(parents=True, exist_ok=True)

        save_path = results_dir / "sensor_detection.png"

        plt.savefig(save_path, dpi=300, bbox_inches="tight")

        print(f"\nGraph saved to: {save_path}")

    plt.show()
    plt.close(fig)
