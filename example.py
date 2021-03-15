import subprocess
import json

import blockscope

with subprocess.run(["tree", "-ixpsugJ", "."], capture_output=True) as data:
	tree = json.loads(data.stdout.decode())

print(tree)
