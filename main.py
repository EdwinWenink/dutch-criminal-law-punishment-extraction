import os

import hydra
from omegaconf import DictConfig, OmegaConf

from src.pipeline import run_pipeline


@hydra.main(config_path="config", config_name="config")
def main(config: DictConfig) -> None:
    # Delayed import for tab completion, see here: https://github.com/facebookresearch/hydra/issues/934
    from src import utils
    # Load optional utilities:
    # - easier access to debug mode
    utils.extras(config)

    # Pretty print config using Rich library
    if config.get("print_config"):
        utils.print_config(config, resolve=True, fields=list(config.keys()))
    else:
        print(OmegaConf.to_yaml(config))

    print(f"Hydra working directory: {os.getcwd()}")

    # Pipeline
    run_pipeline(config)


if __name__ == "__main__":
    main()
