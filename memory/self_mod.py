import yaml

CONFIG_PATH = "config.yaml"

def update_sync_interval(new_interval):
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    config["sync_interval"] = new_interval

    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f)

    print(f"[🧠] Updated sync interval to {new_interval} seconds.")
