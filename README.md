# rmd-helper
`recordmydesktop` helper

Minimalistic wrapper for `recordmydesktop` that makes recording of the currently active screen or a region easier. Designed for single or dual monitor setup, with a resolution of 1920x1080.

# Options
- `--rect`: Select a rectangle for capture (default)
- `--screen`: Capture active screen
- Execution while `recordmydesktop` is running will stop the current recording by sending `SIGTERM`.
