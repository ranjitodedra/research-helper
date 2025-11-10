def convert_path(path_str: str, idx2label: dict[int, str], in_sep: str = "->", out_sep: str = " -> ") -> str:
    """
    Convert a numeric node path string into a labeled path using idx2label.

    - Ignores empty segments from trailing separators.
    - Leaves unknown indices as-is.
    """
    raw = [seg.strip() for seg in path_str.split(in_sep)]
    raw = [seg for seg in raw if seg]  # drop empties from trailing arrow

    out = []
    for seg in raw:
        if seg.isdigit():
            out.append(idx2label.get(int(seg), seg))
        else:
            out.append(seg)
    return out_sep.join(out)


if __name__ == "__main__":
    idx2label = {
        0: "D",
        1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8",
        9: "BSS1", 10: "BSS2",
        11: "C1", 12: "C2", 13: "C3", 14: "C4", 15: "C5", 16: "C6", 17: "D2"
    }

    path = "0->1->11->10->12->7->16->8->15->6->13->14->2->17"
    labeled = convert_path(path, idx2label)
    print(labeled)
    # Output: D -> 1 -> C1 -> 4 -> C2 -> 7 -> C6 -> 8 -> C5 -> 5 -> C3 -> C4 -> 2 -> D2
