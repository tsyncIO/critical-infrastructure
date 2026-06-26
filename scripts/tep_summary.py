import pyreadr
from pathlib import Path
import pandas as pd
path = Path(r"C:/Users/User/Desktop/RobiulGermany/project-26/openbmc-validator/Data/TEP_Faulty_Testing.RData")
print('loading', path)
res = pyreadr.read_r(str(path))
print('keys', list(res.keys()))
df = res[list(res.keys())[0]]
print('shape', df.shape)
print('columns', df.columns[:10].tolist())
print('faultNumber unique', df['faultNumber'].nunique())
print('simulationRun unique', df['simulationRun'].nunique())
print('sample unique', df['sample'].nunique())
print('group counts example')
print(df.groupby(['faultNumber','simulationRun']).size().head(20))
