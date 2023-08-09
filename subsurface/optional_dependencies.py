def require_omf():
    try:
        import omfvista
    except ImportError:
        raise ImportError("The omfvista package is required to run this function.")
    return omfvista
