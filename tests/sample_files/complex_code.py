"""A Python module with high cyclomatic complexity and deep nesting for Radon complexity testing."""


def deeply_nested_processor(data, mode, strict=False, filter_zeros=True, retry_count=3):
    """Processes multi-dimensional matrix with nested conditionals and loops."""
    results = []
    for i in range(len(data)):
        row = data[i]
        if row is not None:
            for j in range(len(row)):
                cell = row[j]
                if cell > 0:
                    if mode == "double":
                        results.append(cell * 2)
                    elif mode == "square":
                        if strict and cell > 100:
                            results.append(100)
                        else:
                            results.append(cell ** 2)
                    elif mode == "modulo":
                        if cell % 2 == 0:
                            results.append(cell // 2)
                        elif cell % 3 == 0:
                            results.append(cell // 3)
                        else:
                            results.append(cell)
                    else:
                        results.append(cell)
                elif cell == 0:
                    if not filter_zeros:
                        results.append(0)
                else:
                    if strict:
                        raise ValueError(f"Negative value: {cell}")
                    else:
                        results.append(-1)
    return results
