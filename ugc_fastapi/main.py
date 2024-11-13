from pathlib import Path
import json

import uvicorn

from src.core.config import BASE_DIR


config_file = str(BASE_DIR) + '/logs/config.json'

with open(config_file) as config:
    config = json.load(config)


if __name__ == '__main__':
    uvicorn.run(
        'src.app:application',
        host='0.0.0.0',
        port=8000,
        reload=True,
        workers=4,
        log_config=config,
    )
