idx2label = {
    0: "D",
    1: "1",
    2: "2",
    3: "C1",
    4: "C2",
    5: "BSS1",
    6: "3",
    7: "4",
    8: "C3",
    9: "C4",
    10: "BSS2",
    11: "BSS3",
    12: "C5",
    13: "5",
    14: "C6",
    15: "C7",
    16: "BSS4",
    17: "6",
    18: "7",
    19: "8",
    20: "C8",
    21: "BSS5",
    22: "9",
    23: "10",
    24: "C9",
    25: "C10",
}

def build_indicator_vectors(idx2label: dict):
    n = len(idx2label)
    customer_list = [0] * n
    bss_list = [0] * n

    for idx, label in idx2label.items():
        if label.startswith("BSS"):
            bss_list[idx] = 1
        if label.startswith("C"):
            customer_list[idx] = 1

    # add one extra 0 at the end
    customer_list.append(0)
    bss_list.append(0)

    return customer_list, bss_list


customers, bss = build_indicator_vectors(idx2label)

print("Station =", bss)
print("Costumer =", customers)

