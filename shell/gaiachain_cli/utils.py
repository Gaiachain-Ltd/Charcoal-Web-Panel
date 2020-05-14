def save_jwt(config_file, jwt):
    with open(config_file, "w") as cfg:
        cfg.write(jwt)


def get_jwt(config_file):
    try:
        with open(config_file) as cfg:
            return cfg.readline()
    except FileNotFoundError:
        pass
