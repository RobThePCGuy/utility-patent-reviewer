# Setting Environment Variables

This guide shows how to set environment variables for API keys on different platforms.

## Windows (PowerShell)

Set permanently for your user account:

```powershell
[System.Environment]::SetEnvironmentVariable('VARIABLE_NAME', 'your_value_here', 'User')
```

**Verify:**
```powershell
$env:VARIABLE_NAME
```

**Note:** Restart any open terminals/applications for changes to take effect.

## Linux/macOS

### Bash

Add to `~/.bashrc` for persistence:

```bash
echo 'export VARIABLE_NAME="your_value_here"' >> ~/.bashrc
source ~/.bashrc
```

### Zsh

Add to `~/.zshrc` for persistence:

```bash
echo 'export VARIABLE_NAME="your_value_here"' >> ~/.zshrc
source ~/.zshrc
```

### Fish

Add to Fish config for persistence:

```bash
echo 'set -gx VARIABLE_NAME "your_value_here"' >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

### Temporary (Current Session Only)

```bash
export VARIABLE_NAME="your_value_here"
```

## Verify Setup

Check that the variable is set:

```bash
# Linux/macOS
echo $VARIABLE_NAME

# Windows PowerShell
$env:VARIABLE_NAME
```

## Common Variables for This Project

- `PATENTSVIEW_API_KEY` - PatentsView Search API key
- `USPTO_API_KEY` - USPTO Open Data Portal API key
