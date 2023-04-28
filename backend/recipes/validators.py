from django.core.validators import RegexValidator

color_regex = RegexValidator(
    r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
    'Enter a valid HEX-code. Example: #49B64E.'
)
