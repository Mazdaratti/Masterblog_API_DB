from pathlib import Path
import os

CUR_DIR = Path(__file__).parent
PATH = "sqlite:///" + str(os.path.join(CUR_DIR, 'blog.sqlite3'))