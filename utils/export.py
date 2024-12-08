def create_m3u(df):
    lines = ["#EXTM3U"]
    for _, row in df.iterrows():
        lines.append(f"#EXTINF:-1,{row['Channel']} - {row['Match']}")
        lines.append(f"acestream://{row['AceStream Link']}")
    return "\n".join(lines)