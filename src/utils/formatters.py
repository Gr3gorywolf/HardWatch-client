def format_storage(value_gb):
    """Format storage values, converting to TB if >= 1000GB"""
    if value_gb >= 1000:
        return f"{value_gb / 1000:.1f}TB"
    return f"{value_gb}GB"