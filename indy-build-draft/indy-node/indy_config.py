import os

# Current network
NETWORK_NAME = os.getenv('INDY_NETWORK_NAME', 'MESH')

# Disable stdout logging
enableStdOutLogging = os.getenv('INDY_ENABLE_STDOUT', True)

# Directory to store ledger.
LEDGER_DIR = os.getenv('INDY_LEDGER_DIR', '/var/lib/indy/ledger')

# Directory to store logs.
LOG_DIR = os.getenv('INDY_LOG_DIR', '/var/log/indy')

# Directory to store keys.
KEYS_DIR = os.getenv('INDY_KEYS_DIR', '/var/lib/indy/keys')

# Directory to store genesis transactions files.
GENESIS_DIR = os.getenv('INDY_GENESIS_DIR', '/var/lib/indy/genesis')

# Directory to store backups.
BACKUP_DIR = os.getenv('INDY_BACKUP_DIR', '/var/lib/indy/backup')

# Directory to store plugins.
PLUGINS_DIR = os.getenv('INDY_PLUGINS_DIR', '/var/lib/indy/plugins')

# Directory to store node info.
NODE_INFO_DIR = os.getenv('INDY_NODE_INFO_DIR', '/var/lib/indy/node')
