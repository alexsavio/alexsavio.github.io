# fancy-terminal

A terminal-styled theme for Pelican, inspired by [daita.io](https://daita.io/).

## Features

- Terminal window aesthetic with title bar buttons (close/minimize/maximize)
- Command prompt style navigation (`user@host:~$`)
- `ls -la` styled menu with permissions and descriptions
- Blinking cursor effect
- Customizable colors via theme variables
- Light and dark theme support
- Responsive design
- Syntax highlighting for code blocks (Pygments compatible)

## Installation

Copy the `fancy-terminal` folder to your Pelican themes directory and set it in your `pelicanconf.py`:

```python
THEME = 'themes/fancy-terminal'
```

## Configuration

### Theme Mode

Enable light burgundy theme (default is dark with green text):

```python
THEME_LIGHT_MODE = True
```

### Custom Colors

Override colors using the `THEME_COLORS` dictionary:

```python
THEME_COLORS = {
    'bg_color': '#f7f7f7',        # Light gray background
    'terminal_bg': '#ffffff',    # Pure white terminal window
    'text_color': '#2d3748',     # Dark blue-gray text
    'primary_color': '#00d4aa',  # Bright cyan-green (terminal green)
    'accent_color': '#ff6b6b',   # Coral red for accents
    'muted_color': '#718096',    # Medium gray for muted elements
    'code_bg': '#f1f5f9',        # Light blue-gray for code blocks
    'link_color': '#00d4aa',     # Same as primary
    'header_bg': '#e2e8f0',      # Light blue header
}
```

### Terminal Prompt Customization

```python
TERMINAL_USER = 'alex'       # Username in prompt (default: AUTHOR lowercase)
TERMINAL_HOST = 'system'     # Hostname in prompt (default: 'blog')
TERMINAL_TITLE = 'zsh'       # Terminal title bar text (default: 'bash')
```

### Menu Configuration

```python
DISPLAY_PAGES_ON_MENU = True
DISPLAY_CATEGORIES_ON_MENU = True

MENUITEMS = [
    ('About', '/about'),
    ('Projects', '/projects'),
]

SOCIAL = [
    ('GitHub', 'https://github.com/username'),
    ('Twitter', 'https://twitter.com/username'),
]
```

## Color Presets

### Dark Green (Classic Terminal)

```python
THEME_LIGHT_MODE = False  # or omit
THEME_COLORS = {
    'bg_color': '#1a1a1a',
    'text_color': '#00ff00',
    'primary_color': '#00ff00',
    'accent_color': '#00cc00',
    'muted_color': '#666666',
    'code_bg': '#0d0d0d',
    'link_color': '#00ff00',
}
```

### Light Burgundy (Default Light Theme)

```python
THEME_LIGHT_MODE = True
# Uses built-in burgundy (#800020) as primary color
```

### Nerdy Light Terminal (Retro Computing)

```python
THEME_LIGHT_MODE = True
THEME_COLORS = {
    'bg_color': '#f7f7f7',        # Light gray background
    'terminal_bg': '#ffffff',    # Pure white terminal window
    'text_color': '#2d3748',     # Dark blue-gray text
    'primary_color': '#00d4aa',  # Bright cyan-green (terminal green)
    'accent_color': '#ff6b6b',   # Coral red for accents
    'muted_color': '#718096',    # Medium gray for muted elements
    'code_bg': '#f1f5f9',        # Light blue-gray for code blocks
    'link_color': '#00d4aa',     # Same as primary
    'header_bg': '#e2e8f0',      # Light blue header
}
```

### Amber/Orange

```python
THEME_COLORS = {
    'bg_color': '#1a1a1a',
    'text_color': '#ffb000',
    'primary_color': '#ffb000',
    'accent_color': '#ff8c00',
    'muted_color': '#666666',
    'code_bg': '#0d0d0d',
    'link_color': '#ffb000',
}
```

### Solarized Dark

```python
THEME_COLORS = {
    'bg_color': '#002b36',
    'text_color': '#839496',
    'primary_color': '#268bd2',
    'accent_color': '#2aa198',
    'muted_color': '#586e75',
    'code_bg': '#073642',
    'link_color': '#268bd2',
}
```

## Example pelicanconf.py

```python
SITENAME = 'My Tech Blog'
SITESUBTITLE = 'Welcome to my terminal'
AUTHOR = 'Alexandre Savio'

THEME = 'themes/fancy-terminal'
THEME_LIGHT_MODE = True

TERMINAL_USER = 'alex'
TERMINAL_HOST = 'blog'

DISPLAY_PAGES_ON_MENU = True
DISPLAY_CATEGORIES_ON_MENU = False

SOCIAL = [
    ('GitHub', 'https://github.com/alexsavio'),
    ('LinkedIn', 'https://linkedin.com/in/alexsavio'),
]
```

## Template Structure

```text
fancy-terminal/
├── static/
│   └── css/
│       └── style.css
├── templates/
│   ├── analytics.html
│   ├── archives.html
│   ├── article.html
│   ├── author.html
│   ├── base.html
│   ├── category.html
│   ├── footer.html
│   ├── index.html
│   ├── page.html
│   ├── pagination.html
│   ├── post.html
│   └── tag.html
└── README.md
```

## License

MIT License
