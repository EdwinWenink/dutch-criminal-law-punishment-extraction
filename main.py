import os
import hydra
from omegaconf import DictConfig, OmegaConf
from src.pipeline import pipeline


@hydra.main(config_path="src/config", config_name="config")
def main(config: DictConfig) -> None:
    # Delayed import for tab completion, see here: https://github.com/facebookresearch/hydra/issues/934
    from src.utils import utils
    # A couple of optional utilities:
    # - disabling python warnings
    # - easier access to debug mode
    # - forcing debug friendly configuration
    # - forcing multi-gpu friendly configuration
    # You can safely get rid of this line if you don't want those
    utils.extras(config)

    # Pretty print config using Rich library
    if config.get("print_config"):
        utils.print_config(config, resolve=True, fields=list(config.keys()))
    else:
        print(OmegaConf.to_yaml(config))

    print(f"Hydra working directory: {os.getcwd()}")

    # Pipeline
    pipeline(config)


if __name__ == "__main__":
    main()
