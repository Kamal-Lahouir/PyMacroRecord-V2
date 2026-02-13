# Upcoming Features (Priority Order)

## 1. Smart Mouse Movement Grouping in Editor
**Priority: High**

Currently the editor tracks every single pixel of mouse movement, resulting in hundreds/thousands of `cursorMove` lines that are tedious to scroll through and edit.

### Approach Ideas:
- **Path simplification**: Collapse consecutive mouse moves into waypoints (e.g., only keep points where direction changes significantly using the Ramer-Douglas-Peucker algorithm)
- **Grouped display**: Visually group consecutive mouse moves into a single collapsible "Mouse Path" row in the editor, showing start → end coordinates, with ability to expand and see individual points
- **Smart merge on edit**: When editing a mouse path group, allow modifying just the start/end points and interpolate the rest
- **"Simplify Path" action**: A toolbar button to reduce mouse move events by a configurable tolerance while preserving click positions and overall trajectory

> Key constraint: Must not ruin macro replay quality — clicks and their target positions must remain precise.

## 2. Search & Filter in Editor
**Priority: High**

Add ability to search and filter events in the editor:
- Search bar at the top of the event list
- Filter by event type (mouse move, click, keyboard, scroll)
- Filter by parameter values (e.g., find all clicks at a specific region)
- Highlight matching results with navigation (next/previous match)

## 3. Configurable Mouse Movement Tracking Resolution
**Priority: Medium**

Add a recording setting to control how many pixels of movement trigger a new `cursorMove` event:
- Setting: "Track mouse every N pixels" (default: 1, options: 1, 2, 5, 10, 25, 50)
- Located in the Recording section of the sidebar
- Lower values = smoother replay but larger files
- Higher values = smaller files but less precise paths
- This works at recording time (reducing data captured) vs. #1 which works at editing time (simplifying existing data)

## 4. Modern UI Styling
**Priority: Low**

Enhance the visual appearance of the application:
- Modern color scheme and theming (light/dark mode)
- Custom styled widgets (rounded buttons, better spacing)
- Consistent iconography (SVG/PNG icon set)
- Improved typography and padding
- Consider using `ttkbootstrap` or `customtkinter` for modern Tkinter styling
- Smooth transitions and hover effects where possible
