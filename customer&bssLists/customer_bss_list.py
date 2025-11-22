idx2label = {
    0: "D",
    1: "1",
    2: "2",
    3: "BSS1",
    4: "C1",
    5: "C2",
    6: "3",
    7: "4",
    8: "5",
    9: "C3",
    10: "C4",
    11: "BSS2",
    12: "C5",
    13: "6",
    14: "BSS3",
    15: "C6",
    16: "7",
    17: "8",
    18: "C7",
    19: "C8",
    20: "C9",
    21: "BSS4",
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

print("Station:", bss)
print("Costumer:", customers)

