import questionary
from prompt_toolkit.styles import Style

# Define the custom style
anydev_qsty_styles = Style([
    ('qmark', 'bold'),  # Question mark
    ('question', 'bold'),  # Question text
    ('answer', 'fg:#6ab0de'),  # Answer (user input) in soft blue
    ('pointer', 'fg:black bg:yellow bold'),  # Highlighted multichoice options
    ('highlighted', 'fg:black bg:yellow'),  # Highlighted choices
    ('selected', 'fg:black bg:yellow'),  # Selected multichoice options
    ('instruction', 'fg:grey'),  # Instructions
    ('text', 'fg:grey'),  # Informative output
    ('error', 'fg:red bold'),  # Error messages
    ('success', 'fg:green bold'),  # Success messages
    ('warning', 'fg:orange bold')  # Warnings
])