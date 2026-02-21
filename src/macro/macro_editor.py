import copy
import math


class MacroEditor:
    """Pure data-layer for editing macro events.
    Operates on the same dict reference as Macro.macro_events."""

    def __init__(self, macro):
        self.macro = macro
        self._clipboard = []

    @property
    def events(self):
        return self.macro.macro_events.get("events", [])

    def has_events(self):
        return len(self.events) > 0

    def get_event(self, index):
        if 0 <= index < len(self.events):
            return self.events[index]
        return None

    def insert_event(self, index, event_dict):
        self.events.insert(index, event_dict)
        self._mark_unsaved()

    def delete_events(self, indices):
        for i in sorted(indices, reverse=True):
            if 0 <= i < len(self.events):
                self.events.pop(i)
        self._mark_unsaved()

    def move_event(self, from_index, to_index):
        if from_index == to_index:
            return
        if not (0 <= from_index < len(self.events)):
            return
        to_index = max(0, min(to_index, len(self.events) - 1))
        event = self.events.pop(from_index)
        self.events.insert(to_index, event)
        self._mark_unsaved()

    def update_event(self, index, field, value):
        if 0 <= index < len(self.events):
            self.events[index][field] = value
            self._mark_unsaved()

    def update_event_fields(self, index, fields_dict):
        if 0 <= index < len(self.events):
            self.events[index].update(fields_dict)
            self._mark_unsaved()

    def copy_events(self, indices):
        self._clipboard = [copy.deepcopy(self.events[i])
                           for i in sorted(indices)
                           if 0 <= i < len(self.events)]

    def paste_events(self, insert_index):
        if not self._clipboard:
            return 0
        copies = copy.deepcopy(self._clipboard)
        for i, event in enumerate(copies):
            self.events.insert(insert_index + i, event)
        self._mark_unsaved()
        return len(copies)

    def has_clipboard(self):
        return len(self._clipboard) > 0

    # ── Mouse Path Grouping ──────────────────────────────────────────

    def get_cursor_move_groups(self):
        """Identify consecutive runs of cursorMove events for display grouping.

        Returns a list of display items:
          - {"kind": "single", "index": int}
          - {"kind": "group", "start": int, "end": int, "count": int,
             "start_x": int, "start_y": int, "end_x": int, "end_y": int,
             "total_time": float}
        """
        events = self.events
        result = []
        i = 0
        while i < len(events):
            if events[i].get("type") == "cursorMove":
                start = i
                total_time = events[i].get("timestamp", 0)
                while i + 1 < len(events) and events[i + 1].get("type") == "cursorMove":
                    i += 1
                    total_time += events[i].get("timestamp", 0)
                end = i  # inclusive
                count = end - start + 1
                if count >= 2:
                    result.append({
                        "kind": "group",
                        "start": start,
                        "end": end,
                        "count": count,
                        "start_x": events[start].get("x", 0),
                        "start_y": events[start].get("y", 0),
                        "end_x": events[end].get("x", 0),
                        "end_y": events[end].get("y", 0),
                        "total_time": total_time,
                    })
                else:
                    result.append({"kind": "single", "index": start})
            else:
                result.append({"kind": "single", "index": i})
            i += 1
        return result

    def get_path_stats(self, start_idx, end_idx):
        """Return statistics for a cursorMove path segment."""
        events = self.events
        total_time = 0.0
        total_distance = 0.0
        count = end_idx - start_idx + 1

        prev_x = events[start_idx].get("x", 0)
        prev_y = events[start_idx].get("y", 0)
        total_time += events[start_idx].get("timestamp", 0)

        for i in range(start_idx + 1, end_idx + 1):
            x = events[i].get("x", 0)
            y = events[i].get("y", 0)
            total_time += events[i].get("timestamp", 0)
            total_distance += math.hypot(x - prev_x, y - prev_y)
            prev_x, prev_y = x, y

        return {
            "total_moves": count,
            "total_distance": total_distance,
            "total_time": total_time,
            "start_x": events[start_idx].get("x", 0),
            "start_y": events[start_idx].get("y", 0),
            "end_x": events[end_idx].get("x", 0),
            "end_y": events[end_idx].get("y", 0),
        }

    def rescale_group_time(self, start_idx, end_idx, new_total_time):
        """Proportionally rescale all timestamps in a group to match new_total_time.

        Each event's timestamp is scaled by (new_total / old_total) so the
        relative timing between moves is preserved.
        """
        events = self.events
        old_total = sum(
            events[i].get("timestamp", 0) for i in range(start_idx, end_idx + 1)
        )
        if old_total <= 0 or new_total_time < 0:
            return
        scale = new_total_time / old_total
        for i in range(start_idx, end_idx + 1):
            events[i]["timestamp"] = events[i].get("timestamp", 0) * scale
        self._mark_unsaved()

    # ── Ramer-Douglas-Peucker Path Simplification ────────────────────

    @staticmethod
    def _rdp(points, tolerance):
        """Ramer-Douglas-Peucker algorithm.
        points: list of (x, y) tuples
        tolerance: max perpendicular distance threshold
        Returns: list of indices (into points) to keep.
        """
        if len(points) <= 2:
            return list(range(len(points)))

        # Find the point farthest from the line between first and last
        first = points[0]
        last = points[-1]
        max_dist = 0.0
        max_idx = 0

        dx = last[0] - first[0]
        dy = last[1] - first[1]
        line_len_sq = dx * dx + dy * dy

        for i in range(1, len(points) - 1):
            px, py = points[i]
            if line_len_sq == 0:
                # Start and end are the same point
                dist = math.hypot(px - first[0], py - first[1])
            else:
                # Perpendicular distance from point to line
                t = ((px - first[0]) * dx + (py - first[1]) * dy) / line_len_sq
                t = max(0, min(1, t))
                proj_x = first[0] + t * dx
                proj_y = first[1] + t * dy
                dist = math.hypot(px - proj_x, py - proj_y)

            if dist > max_dist:
                max_dist = dist
                max_idx = i

        if max_dist > tolerance:
            # Recursively simplify both halves
            left = MacroEditor._rdp(points[:max_idx + 1], tolerance)
            right = MacroEditor._rdp(points[max_idx:], tolerance)
            # Combine, avoiding duplicate of max_idx
            return left + [idx + max_idx for idx in right[1:]]
        else:
            # All intermediate points are within tolerance, keep only endpoints
            return [0, len(points) - 1]

    def simplify_path(self, start_idx, end_idx, tolerance):
        """Apply RDP simplification to cursorMove events[start_idx..end_idx].

        Preserves start and end points always.
        Recalculates timestamps proportionally for remaining points.
        Returns the number of events removed.
        """
        events = self.events
        count = end_idx - start_idx + 1
        if count <= 2:
            return 0

        # Extract points
        points = [(events[i].get("x", 0), events[i].get("y", 0))
                  for i in range(start_idx, end_idx + 1)]

        # Run RDP
        keep_local = self._rdp(points, tolerance)
        if len(keep_local) >= count:
            return 0  # Nothing to simplify

        # Convert local indices to absolute event indices
        keep_abs = set(start_idx + k for k in keep_local)

        # Compute cumulative distances for timestamp redistribution
        cum_dist = [0.0]
        for i in range(1, count):
            d = math.hypot(
                points[i][0] - points[i - 1][0],
                points[i][1] - points[i - 1][1],
            )
            cum_dist.append(cum_dist[-1] + d)
        total_dist = cum_dist[-1]

        # Total time across the path
        total_time = sum(events[start_idx + i].get("timestamp", 0)
                         for i in range(count))

        # Redistribute timestamps among kept points based on distance fractions
        kept_sorted = sorted(keep_local)
        for j, local_idx in enumerate(kept_sorted):
            abs_idx = start_idx + local_idx
            if j == 0:
                # First kept point gets the original first timestamp
                events[abs_idx]["timestamp"] = events[start_idx].get("timestamp", 0)
            else:
                prev_local = kept_sorted[j - 1]
                if total_dist > 0:
                    frac = (cum_dist[local_idx] - cum_dist[prev_local]) / total_dist
                else:
                    # All points at same position, distribute evenly
                    frac = 1.0 / (len(kept_sorted) - 1)
                events[abs_idx]["timestamp"] = total_time * frac

        # Delete events not in keep set (reverse order to preserve indices)
        to_delete = []
        for i in range(start_idx, end_idx + 1):
            if i not in keep_abs:
                to_delete.append(i)
        for i in reversed(to_delete):
            events.pop(i)

        self._mark_unsaved()
        return len(to_delete)

    def _mark_unsaved(self):
        self.macro.main_app.macro_saved = False
