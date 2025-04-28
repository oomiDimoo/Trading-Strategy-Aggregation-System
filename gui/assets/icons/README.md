# Icons for Trading Strategy Aggregation System

This directory contains icons used throughout the Trading Strategy Aggregation System GUI.

## Icon Set

The following icons are included:

- `add.svg`: Add new item
- `edit.svg`: Edit item
- `delete.svg`: Delete item
- `save.svg`: Save configuration
- `load.svg`: Load configuration
- `run.svg`: Run analysis
- `chart.svg`: Chart visualization
- `dashboard.svg`: Dashboard view
- `strategy.svg`: Strategy icon
- `settings.svg`: Settings icon
- `export.svg`: Export data
- `dropdown.svg`: Dropdown arrow

## Usage

Icons are referenced in the QSS stylesheet and can be used in the application code as follows:

```python
from PyQt5.QtGui import QIcon

# Create an icon from a file
icon = QIcon("assets/icons/add.svg")

# Set the icon on a button
button.setIcon(icon)
```

## Credits

Icons are based on the Material Design icon set with custom modifications for the Trading Strategy Aggregation System.