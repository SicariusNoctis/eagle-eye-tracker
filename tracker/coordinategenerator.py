import time

import numpy as np
import quaternion

from .coordinatemath import (apply_rotation, pos_quats_to_plot_coords)
from .latency import Latency
from .testpaths import test_paths

# TODO modify actual coordinate generator to send between [-1,1] [-1,1] for x, y
# ensure proper aspect ratio that we expect
class CoordinateGenerator:
    """Generates coordinates to simulate a moving object."""

    def __init__(self, coord_getter_func=None):
        self.coord_getter_func = coord_getter_func
        self.coord = (0.0, 0.0)
        self.width  = 0.55
        self.height = 0.4

        self.update(0, quaternion.x, False)

    def draw(self, ax, color="#ff55bb"):
        """Draw a coordinate at location in image frame."""
        ax.scatter3D(*pos_quats_to_plot_coords([self._draw_quat]),
            s=50, color=color)

    def draw_quat(self, ax, color="#ff55bb"):
        """Draw destination on sphere."""
        ax.scatter3D(*pos_quats_to_plot_coords([self.dest_quat]),
            s=50, color=color)

    def update(self, dt, rot, update_coord=True):
        """Updates generated coordinate.

        Args:
            dt (float): Time elapsed since last update() call.
            rot (float): Rotation quaternion to same frame as camera.
        """
        if update_coord:
            self._update_coord(dt, rot)
        v = self._get_offset_quat()
        self._draw_quat = apply_rotation(v, rot)
        self.dest_quat = self._draw_quat / np.abs(self._draw_quat)

    def _get_offset_quat(self):
        """Get position quaternion to express offset from (1,0,0) axis."""
        return np.quaternion(0., 1.,
            -self.width  * self.coord[0],
             self.height * self.coord[1])

    def _update_coord(self, dt, rot):
        """Calculates next coord from coord_getter_func or path."""

        if self.coord_getter_func is not None:
            self.coord = self.coord_getter_func()
            return

        v = test_paths[0].get_next_pos_quat(dt)
        offset = apply_rotation(v, rot.inverse())
        coord = np.clip([
            -offset.y / self.width,
             offset.z / self.height], -1., 1.)
        self.coord = tuple(coord)

class LatentCoordinateGenerator(CoordinateGenerator):
    COORD_LATENCY = 0.200
    coord = Latency(COORD_LATENCY)

    def __init__(self, parent, fps=20):
        self.parent = parent
        self.fps = fps
        self.time_elapsed = 0.0
        self.time_since_update = 0.0
        super().__init__(lambda: self.parent.coord)

    def update(self, dt, rot, update_coord=True):
        # self.parent.update(dt, rot)
        self.time_elapsed += dt
        self.time_since_update += dt
        update_coord = (self.time_since_update >= 1. / self.fps)
        if update_coord:
            self.time_since_update %= 1. / self.fps
        super().update(dt, rot, update_coord)

    def draw(self, ax, color="#772255"):
        """Draw a coordinate at location in image frame."""
        super().draw(ax, color)
        self.parent.draw(ax)

    def draw_quat(self, ax, color="#772255"):
        """Draw destination on sphere."""
        super().draw_quat(ax, color)
        self.parent.draw_quat(ax)

    def _time_func(self):
        return self.time_elapsed
