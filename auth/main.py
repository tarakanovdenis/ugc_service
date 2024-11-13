import json

import uvicorn

from src.core.config import BASE_DIR


log_config_file = str(BASE_DIR) + "/logs/config.json"

with open(log_config_file) as config:
    log_config = json.load(config)


if __name__ == '__main__':
    uvicorn.run(
        'src.app:application',
        host='0.0.0.0',
        port=8000,
        workers=4,
        log_config=log_config,
        reload=True,
    )
