import pyreadr
from pathlib import Path
root = Path(r"C:/Users/User/Desktop/RobiulGermany/project-26/openbmc-validator/Data")
for path in sorted(root.glob("*.RData")):
    print("FILE", path.name)
    result = pyreadr.read_r(str(path))
    print("objects:", list(result.keys()))
    for key,obj in result.items():
        print(" object", key, type(obj).__name__, getattr(obj, "shape", None))
        if hasattr(obj, "columns"):
            print("  cols", list(obj.columns[:20]))
            print("  dtypes", {str(k): str(v) for k,v in obj.dtypes.head(20).to_dict().items()})
            print("  sample", obj.head(1).to_dict(orient="records"))
    print("---")
