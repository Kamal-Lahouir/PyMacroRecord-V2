
## Executive Summary

Macro Recorder (macrorecorder.com) is a professional desktop automation tool for Windows/Mac that records and replays mouse and keyboard actions. The software uses a visual context-based clicking system rather than fixed coordinates, making macros more robust and adaptable.[^1]

## Core Recording Features

### Mouse Recording Capabilities

- **Mouse movements**: Records cursor paths between clicks, consolidated into single manageable actions rather than coordinate dumps[^2][^1]
- **Mouse clicks**: Left-click, right-click, and double-click actions[^1]
- **Scroll wheel actions**: Captures scrolling movements with configurable values[^2][^1]
- **Smart mouse smoothing**: Algorithms transform erratic mouse movements into smooth curves or linear shapes[^1]
- **Visual overlay system**: Displays recorded mouse paths and click positions as overlay graphics on the desktop for easy identification during editing[^2][^1]


### Keyboard Recording Capabilities

- **Text input**: Captures typed text as complete strings[^1]
- **Hotkey presses**: Records individual key combinations and special keys[^3][^1]
- **Key repetition counter**: Tracks number of repetitions for key presses[^2]


### Recording Control

- **Selective recording**: Users can choose what to record (mouse movement, clicks only, keyboard input)[^1]
- **Hotkey start/stop**: Customizable hotkeys to begin and end recording sessions[^1]
- **Visual recording interface**: Red button starts recording, black square stops it[^1]


## Advanced Click System (Key Differentiator)

### Visual Context Recognition

- **Image-based targeting**: Uses visual context around click locations instead of fixed X/Y coordinates[^1]
- **Desktop scanning**: During playback, scans the desktop for captured visual areas and clicks when found[^1]
- **Position tolerance**: Identifies click targets even if they've shifted (e.g., due to ads on web pages)[^1]
- **Smart waiting**: Macro pauses until click target is found, eliminating need for static wait times[^1]


## Macro Editor - Detailed Features

### Action List Interface

- **Chronological display**: All recorded actions shown in sequential order[^2]
- **Action columns**: Type, Label, Comment, and parameter details visible[^2]
- **Line numbers**: Toggle-able line numbering with quick-jump functionality[^2]
- **Visual overlays**: Clicking mouse actions displays the actual path or click position as desktop overlay[^2]


### Editing Operations

- **Double-click editing**: Double-click any action or press ENTER to modify[^3][^2]
- **Multi-selection**: Select multiple actions using CTRL and/or SHIFT keys[^2]
- **Drag \& drop**: Rearrange actions by dragging to new positions[^2]
- **Copy \& paste**: Duplicate actions within or between macro scripts[^2]
- **Delete actions**: Remove single or multiple selected actions with DEL key[^2]


### Action Parameters (Editable Fields)

- **Text**: Character input, variable names, text content[^2]
- **Window title**: Target application window identifier[^2]
- **Application/File**: Focus targets, executable paths[^2]
- **Target label**: Jump markers for goto actions[^2]
- **Timeout label**: Fallback labels when actions fail or timeout[^2]
- **Delay/Timeout**: Sleep durations and timeout values[^2]
- **Target-X/Y**: Mouse position coordinates (for move actions)[^2]
- **Width/Height**: Window dimensions (for focus actions)[^2]
- **Value**: Variable values, mouse wheel scroll amounts[^2]
- **Counter**: Repetition count for key/mouse presses[^2]


### Action Management

#### Grouping System

- **Create groups**: Select multiple actions and press CTRL+G or right-click menu[^2]
- **Collapsible groups**: Expand/collapse with +/- icons, grouped actions are indented[^2]
- **Color coding**: Assign background colors to groups for visual organization (e.g., orange for data collection, red for error handling)[^2]
- **Ungroup**: CTRL+SHIFT+G to dissolve groups[^2]


#### Labels and Navigation

- **Custom labels**: Assign unique text labels to any action as jump markers[^2]
- **Reserved labels**: "Start", "End", and "Next" are system-reserved[^2]
- **Label search**: Click column header and type to find labeled actions[^2]
- **Label dropdown**: Triangle menu shows all available labels for quick navigation[^2]


#### Comments System

- **Action comments**: Add descriptive notes to each action for documentation purposes[^2]


### Search \& Replace

- **Bulk parameter editing**: Change parameters across all actions simultaneously[^2]
- **Works on all parameter types**: Text, window titles, file paths, coordinates, delays, values, counters[^2]


### Manual Action Insertion

- **Hotkey shortcuts**: Quick-add actions using keyboard (C=Click, R=Right-Click, M=Move, S=Scroll, T=Text, H=Hotkey, P=Pixel, G=Goto, W=Wait)[^4]
- **Toolbar icons**: Click action icons in main menu[^4]
- **Context menu**: Right-click in action list to insert actions[^4]
- **Position control**: Highlight existing action to insert new action underneath it[^4]


## Window Management

### Focus Control

- **Window tracking**: Records window positions and sizes during recording[^1]
- **Auto-restoration**: Restores window positions and sizes during playback for precise execution[^1][^2]
- **Focus switching**: Ability to switch focus to specific applications[^2]


## Control Flow Actions

### Jump and Loop Controls

- **Goto**: Jump to specific labeled sections in macro[^2]
- **Repeat**: Execute macro sections multiple times[^2]
- **Conditional logic**: Pixel color detection can trigger jumps to specific labels[^2]


### Wait Actions

- **Timed delays**: Static wait periods with configurable duration[^2]
- **Smart waiting**: Wait for visual elements to appear before proceeding[^1]


## Playback Features

### Execution Control

- **Hotkey playback**: Start macro with customizable hotkey (default F3 to stop in PyMacroRecord)[^1]
- **Variable speed**: Adjust playback speed for faster/slower execution[^1]
- **Infinite repeat**: Loop macros unlimited times[^1]
- **Breakpoints**: Toggle breakpoints by double-clicking line numbers[^2]


### Playback Options

- **Interval timing**: Set delays between repetitions[^1]
- **Scheduled execution**: Time/date-based macro triggers[^5]
- **Post-playback actions**: Options like standby or shutdown after completion[^1]


## File Management

### Save/Load System

- **Universal format**: JSON-based file format for cross-platform compatibility[^1]
- **Save recordings**: Export macros as reusable files[^1]
- **Load macros**: Import previously saved automation scripts[^1]
- **Sharing**: Share macro files with team members[^1]


## PyMacroRecord Current Feature Comparison

### Existing Features in PyMacroRecord

- Basic mouse recording (movement, clicks)[^1]
- Keyboard input recording[^1]
- Smooth mouse recording[^1]
- Customizable hotkeys for record/playback[^1]
- Variable playback speed[^1]
- Infinite repeat with intervals[^1]
- JSON-based save/load system[^1]
- Post-playback actions (standby/shutdown)[^1]
- Selective recording options[^1]
- GUI built with tkinter[^1]


### Missing Features (Gap Analysis)

#### Critical Missing Features

1. **Visual context-based clicking** - PyMacroRecord uses fixed coordinates; Macro Recorder uses image recognition
2. **Macro editor interface** - No comprehensive editing UI with action list view
3. **Manual action insertion** - Cannot add individual actions after recording
4. **Action grouping and organization** - No grouping, color coding, or collapsing features
5. **Labels and goto** - No jump markers or control flow
6. **Search \& replace** - No bulk editing functionality
7. **Window position management** - No automatic window restoration
8. **Visual overlays** - No desktop overlay system to visualize recorded actions

#### Moderate Missing Features

1. **Comments system** - No per-action documentation
2. **Line numbers and breakpoints** - No debugging tools
3. **Drag \& drop editing** - Limited action rearrangement
4. **Multi-selection editing** - Cannot edit multiple actions simultaneously
5. **Action parameter table** - No detailed parameter editing interface
6. **Label navigation** - No quick-jump to labeled sections

## Recommended PRD for PyMacroRecord Enhancement

### Phase 1: Core Editor Infrastructure

1. **Action list view**: Display recorded actions in editable table format with columns for action type, parameters, labels, comments
2. **Double-click editing**: Open parameter editing dialog for any action
3. **Multi-selection**: CTRL/SHIFT selection support for batch operations
4. **Drag \& drop**: Reorder actions visually
5. **Delete selected**: Remove one or multiple actions
6. **Line numbering**: Add line numbers with click-to-jump functionality

### Phase 2: Action Management

1. **Manual action insertion**: Add mouse clicks, keystrokes, waits, etc. after recording
2. **Hotkey quick-add**: Keyboard shortcuts for common action types
3. **Labels system**: Add text labels to actions for navigation
4. **Comments**: Per-action comment field
5. **Copy/paste actions**: Duplicate actions within macro

### Phase 3: Advanced Organization

1. **Action grouping**: CTRL+G to group selections, collapsible groups
2. **Color coding**: Assign colors to groups for visual organization
3. **Search \& replace**: Bulk parameter editing across actions
4. **Goto/repeat actions**: Control flow with labeled jumps
5. **Conditional logic**: Basic if/then based on conditions

### Phase 4: Visual Enhancements

1. **Mouse path consolidation**: Combine movements between clicks into single actions
2. **Parameter editing UI**: Dedicated parameter table for each action type
3. **Visual overlays** (advanced): Desktop overlay showing recorded paths/clicks
4. **Breakpoint system**: Debug macros step-by-step

### Phase 5: Smart Features (Long-term)

1. **Image-based clicking**: Visual context recognition instead of fixed coordinates
2. **Window management**: Track and restore window positions
3. **Smart waiting**: Wait for visual elements instead of fixed delays

## Technical Implementation Notes

### Data Structure Recommendations

```
Action {
  type: "click" | "right_click" | "mouse_move" | "scroll" | "text_input" | "hotkey" | "wait" | "goto"
  parameters: {
    // Action-specific parameters
    x, y, text, keys, delay, target_label, etc.
  }
  label: string | null
  comment: string | null
  group_id: string | null
  enabled: boolean
}

Group {
  id: string
  name: string
  color: string | null
  collapsed: boolean
}
```


### UI Components Needed

- Action list TreeView/Table widget
- Parameter editor dialog
- Label management sidebar
- Group color picker
- Search/replace dialog
- Toolbar with action icons

This PRD provides a comprehensive roadmap for enhancing PyMacroRecord with professional editing capabilities while maintaining its open-source, free nature.[^1]

