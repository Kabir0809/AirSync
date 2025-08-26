# AirSync Game Shortcuts Feature

This document explains how to use the Game Shortcuts feature in AirSync.

## Overview

The Game Shortcuts feature allows you to add, manage, and launch shortcuts to your installed games directly from the AirSync interface. This makes it easy to quickly access your favorite racing games while using hand gesture controls.

## Features

### 1. Add Games

- Click the "Add Game" button in the Game Shortcuts section
- Browse for game executables or use auto-detection
- Set custom command line arguments if needed
- Games are automatically saved to games.json

### 2. Auto-Detection

- The "Scan" button automatically detects popular racing games
- Searches common installation directories (Steam, Epic Games, Origin, etc.)
- Supports games like Forza, Need for Speed, F1, Dirt Rally, and more

### 3. Launch Games

- Click the "Launch" button next to any game
- Tracks play count and last played time
- Opens games with configured arguments

### 4. Edit Games

- Click the "Edit" button to modify game details
- Change name, path, or arguments
- Updates are saved automatically

### 5. Delete Games

- Click the "Delete" button to remove games
- Confirmation dialog prevents accidental deletion

## File Structure

### games.json

This file stores all your game shortcuts and is automatically created in the application directory.

```json
[
  {
    "Id": "12345678-1234-1234-1234-123456789abc",
    "Name": "Forza Horizon 5",
    "Path": "C:\\Program Files\\Steam\\steamapps\\common\\ForzaHorizon5\\ForzaHorizon5.exe",
    "Arguments": "",
    "LastPlayed": "2024-01-01T12:00:00",
    "PlayCount": 5
  }
]
```

### Supported Game Patterns

The auto-detection feature searches for these game patterns:

- Forza Horizon (_ForzaHorizon_.exe)
- Forza Motorsport (_ForzaMotorsport_.exe)
- Need for Speed (_NeedForSpeed_.exe, _NFS_.exe)
- F1 (_F1\__.exe, _F1_.exe)
- Dirt Rally (_DirtRally_.exe, _dirt_.exe)
- Assetto Corsa (_AssettoCorsa_.exe, _acs_.exe)
- Project CARS (_pCARS_.exe, _ProjectCARS_.exe)
- Burnout (_Burnout_.exe)
- The Crew (_TheCrew_.exe)

### Search Directories

Auto-detection searches these common directories:

- C:\Program Files (x86)\Steam\steamapps\common
- C:\Program Files\Steam\steamapps\common
- C:\Program Files (x86)\Epic Games
- C:\Program Files\Epic Games
- C:\Program Files (x86)\Origin Games
- C:\Program Files\Origin Games
- C:\Program Files (x86)\EA Games
- C:\Program Files\EA Games

## Usage Tips

1. **Use Auto-Detection First**: Start with the "Scan" button to automatically find installed games
2. **Manual Addition**: If auto-detection doesn't find your game, use "Add Game" to browse manually
3. **Command Line Arguments**: Some games may require specific launch arguments (e.g., `-windowed`, `-dx11`)
4. **Organization**: Use descriptive names to easily identify your games
5. **Backup**: The games.json file can be backed up to preserve your shortcuts

## Troubleshooting

### Game Won't Launch

- Verify the game path is correct
- Check if the game requires administrator privileges
- Ensure the game executable exists and is not corrupted

### Auto-Detection Not Working

- Make sure games are installed in standard directories
- Try running AirSync as administrator if needed
- Some games may need manual addition

### Games Not Showing

- Check if games.json exists in the application directory
- Verify the JSON format is valid
- Restart AirSync to reload the games list

## Integration with Hand Gestures

The Game Shortcuts feature works seamlessly with AirSync's hand gesture controls:

1. Launch your racing game using the shortcuts
2. Click "START" to begin hand gesture detection
3. Use natural hand movements to control your game
4. Games will remember your play statistics

This feature makes AirSync a complete gaming solution for racing enthusiasts who want both convenient game management and innovative gesture controls.
