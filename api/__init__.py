from api.config  import PACKAGE_ROOT
# Create version variable
with open(PACKAGE_ROOT/ "VERSION","r") as version_file:
    __version__ = version_file.read().strip()