def compute_counts(total_nodes: int):
    # Ratios based on your example: 4:2:4  ->  2:1:2
    customers = round(0.4 * total_nodes)   # 40%
    bss = round(0.2 * total_nodes)         # 20%
    intersections = total_nodes - customers - bss  # whatever is left

    return customers, bss, intersections


if __name__ == "__main__":
    n = int(input("Enter total number of nodes: "))
    customers, bss, intersections = compute_counts(n)

    print(f"Total nodes      : {n}")
    print(f"Customer nodes   : {customers}")
    print(f"BSS nodes        : {bss}")
    print(f"Intersection nodes: {intersections}")
