def preprocessing_filter_account(endpoints):
    filtered = []
    for (path, path_regex, method, callback) in endpoints:
        # Remove all but DRF API endpoints
        if "api/v1.1/account" in path:
            filtered.append((path, path_regex, method, callback))
    return filtered


def preprocessing_filter_organization(endpoints):
    filtered = []
    for (path, path_regex, method, callback) in endpoints:
        # Remove all but DRF API endpoints
        if "api/v1.1/organization" in path:
            filtered.append((path, path_regex, method, callback))
    return filtered