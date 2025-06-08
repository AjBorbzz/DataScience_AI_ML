### Setup rosetta_env for this directory for compatibility of other tools

**Create a virtual environment in Rosetta mode:**

```shell
arch -x86_64 /usr/bin/python3 -m venv rosetta_env
source rosetta_env/bin/activate
```

 install older packages with fewer compatibility issues:

 ```shell
 pip install pmdarima
 ```

> Note: I have `rosetta_env` locally
