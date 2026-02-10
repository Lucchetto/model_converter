from enum import StrEnum

class AppPlatform(StrEnum):
    Android = "android"
    Desktop = "desktop"
    MacOS = "macos"
    
    @classmethod
    def from_value(cls, value):
        """Get the enum constant for the given value, or None if the value doesn't exist."""
        return cls(value) if value in cls._value2member_map_ else None