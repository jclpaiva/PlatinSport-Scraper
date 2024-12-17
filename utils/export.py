import pandas as pd

def create_m3u(df: pd.DataFrame) -> str:
    """
    Create an M3U playlist from the given DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing match and stream information.

    Returns:
        str: M3U playlist content as a string.
    """
    lines = ["#EXTM3U"]
    for _, row in df.iterrows():
        lines.append(f"#EXTINF:-1,{row['Channel']}")
        lines.append(f"acestream://{row['AceStream Link']}")
    return "\n".join(lines)

