import os
import json
import subprocess
import sys
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_mechanism(mech_dir: str) -> bool:
    """
    Generate a temporary MusicBox configuration and run it for a mechanism.

    Parameters
    ----------
    mech_dir : str
        The path to the mechanism directory containing a config.yaml file.

    Returns
    -------
    bool
        True if the mechanism ran successfully, False otherwise.
    """
    logger.info("Testing mechanism in %s...", mech_dir)
    config_yaml_path = os.path.join(mech_dir, "config.yaml")
    if not os.path.exists(config_yaml_path):
        logger.warning("No config.yaml found in %s", mech_dir)
        return False

    music_box_config: Dict[str, Any] = {
        "box model options": {
            "grid": "box",
            "chemistry time step [min]": 1.0,
            "output time step [min]": 1.0,
            "simulation length [day]": 0.001
        },
        "initial conditions": {},
        "environmental conditions": {
            "temperature": {
                "initial value [K]": 298.15
            },
            "pressure": {
                "initial value [Pa]": 101325.0
            }
        },
        "model components": [
            {
                "type": "CAMP",
                "configuration file": "config.yaml"
            }
        ]
    }

    config_file_path = os.path.join(mech_dir, "music_box_config_temp.json")
    with open(config_file_path, 'w') as f:
        json.dump(music_box_config, f)

    try:
        result = subprocess.run(
            ["music_box", "-c", "music_box_config_temp.json"],
            cwd=mech_dir,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error("Error running music-box for %s:", mech_dir)
            logger.error(result.stderr)
            logger.debug(result.stdout)
            return False
        else:
            logger.info("Successfully ran mechanism in %s", mech_dir)
            return True
    except Exception as e:
        logger.error("Exception while testing %s: %s", mech_dir, e)
        return False
    finally:
        if os.path.exists(config_file_path):
            os.remove(config_file_path)

def main() -> None:
    """
    Find all mechanisms in the mech directory and test them.

    Returns
    -------
    None
    """
    mech_root: str = "mech"
    if not os.path.exists(mech_root):
        logger.error("Mechanism root directory '%s' not found.", mech_root)
        sys.exit(1)

    success: bool = True
    mechanisms_found: int = 0

    try:
        entries: List[str] = os.listdir(mech_root)
    except OSError as e:
        logger.error("Could not list directory %s: %s", mech_root, e)
        sys.exit(1)

    for entry in entries:
        mech_dir = os.path.join(mech_root, entry)
        if os.path.isdir(mech_dir):
            mechanisms_found += 1
            if not test_mechanism(mech_dir):
                success = False

    if mechanisms_found == 0:
        logger.error("No mechanisms found to test.")
        sys.exit(1)

    if not success:
        logger.error("Some mechanisms failed to run.")
        sys.exit(1)
    else:
        logger.info("All mechanisms passed.")

if __name__ == "__main__":
    main()
