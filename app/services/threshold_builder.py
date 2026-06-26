import pandas as pd


def derive_thresholds(df: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = [c for c in df.columns if c.startswith('xmeas_') or c.startswith('xmv_')]
    stats = []
    for variable in numeric_columns:
        series = df[variable].dropna()
        if series.empty:
            continue
        mean = series.mean()
        std = series.std()
        q001 = series.quantile(0.001)
        q005 = series.quantile(0.005)
        q025 = series.quantile(0.025)
        q500 = series.quantile(0.5)
        q975 = series.quantile(0.975)
        q995 = series.quantile(0.995)
        q999 = series.quantile(0.999)
        if q005 == q995 or std == 0 or pd.isna(std):
            warning_low = mean - 3 * std if pd.notna(std) else mean
            warning_high = mean + 3 * std if pd.notna(std) else mean
            critical_low = mean - 4 * std if pd.notna(std) else mean
            critical_high = mean + 4 * std if pd.notna(std) else mean
        else:
            warning_low = q005
            warning_high = q995
            critical_low = q001
            critical_high = q999
        if warning_low == warning_high:
            warning_low = mean - 3 * std
            warning_high = mean + 3 * std
        stats.append({
            'variable_name': variable,
            'baseline_mean': mean,
            'baseline_std': std,
            'q001': q001,
            'q005': q005,
            'q025': q025,
            'q500': q500,
            'q975': q975,
            'q995': q995,
            'q999': q999,
            'warning_low': warning_low,
            'warning_high': warning_high,
            'critical_low': critical_low,
            'critical_high': critical_high,
        })
    return pd.DataFrame(stats)
