import pyreadr
from pathlib import Path

OUTPUT_FILE = Path('reports/tep_data_inspection.md')
DATA_DIR = Path('Data')


def inspect_file(path: Path) -> str:
    result = pyreadr.read_r(str(path))
    lines = [f'# Inspection for {path.name}', '']
    if not result:
        lines.append('No tabular objects found.')
        return '\n'.join(lines)
    for key, obj in result.items():
        lines.append(f'## Object: {key}')
        lines.append(f'- type: {type(obj).__name__}')
        lines.append(f'- shape: {getattr(obj, "shape", None)}')
        if hasattr(obj, 'columns'):
            lines.append('- columns:')
            for col in list(obj.columns):
                lines.append(f'  - {col}')
            lines.append('- dtypes:')
            for col, dtype in obj.dtypes.items():
                lines.append(f'  - {col}: {dtype}')
            lines.append('- sample rows:')
            sample = obj.head(3).fillna('').to_dict(orient='records')
            for row in sample:
                lines.append(f'  - {row}')
    return '\n'.join(lines)


if __name__ == '__main__':
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    lines = ['# TEP Data Inspection Report', '']
    for path in sorted(DATA_DIR.glob('*.RData')):
        lines.append(inspect_file(path))
        lines.append('\n---\n')
    OUTPUT_FILE.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Written inspection report to {OUTPUT_FILE}')
