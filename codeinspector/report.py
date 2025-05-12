def summarize_analysis(results: list[dict[str, float]]) -> str:
    if not results:
        return "No Python files analyzed."

    summary = ["\nProject Analysis Summary:"]
    summary.append(f"Analyzed {len(results)} Python files.\n")

    avg_complexity = sum(r["complexity"] for r in results) / len(results)
    avg_maintainability = sum(r["maintainability"] for r in results) / len(results)
    total_flake8 = sum(r["flake8_issues"] for r in results)

    summary.append(f"Average Cyclomatic Complexity: {avg_complexity:.2f}")
    summary.append(f"Average Maintainability Index: {avg_maintainability:.2f}")
    summary.append(f"Total Flake8 Issues: {total_flake8}")

    summary.append("\nFile-wise Details:")
    for r in results:
        summary.append(
            f"- {r['file']}: Complexity={r['complexity']:.2f}, "
            f"Maintainability={r['maintainability']:.2f}, Flake8 Issues={r['flake8_issues']}"
        )

    return "\n".join(summary)
