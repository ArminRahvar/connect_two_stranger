from types import SimpleNamespace
from src.utils.keyboard import create_keybord


keys = SimpleNamespace(
    random_connect=':bust_in_silhouette: Random Connect',
    settings=':gear: Settigs',
    exit=':cross_mark: Exit'
)

keyboards = SimpleNamespace(
    main=create_keybord(keys.random_connect, keys.settings),
    exit=create_keybord(keys.exit)
)

states = SimpleNamespace(
    random_connect='Random_Connect',
    main='main',
    connected='connected'
)
