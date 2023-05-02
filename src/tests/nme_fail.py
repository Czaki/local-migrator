import sys

try:
    import local_migrator  # noqa: F401
except ImportError as e:
    if e.args[0].startswith("local_migrator is incompatible with nme<=0.1.6. You need to upgrade or uninstall nme."):
        print("Ok")
        sys.exit(0)
print("ImportError not raised")
sys.exit(1)
