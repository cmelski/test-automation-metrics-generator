def generate_insights(defects, fail_rates, coverage):
    insights = []

    for area in defects:
        if area["count"] > 10:
            insights.append(f"{area['area']} has high defect volume → increase test coverage")

    for area in fail_rates:
        if area["fail_rate"] > 0.3:
            insights.append(f"{area['area']} has high failure rate → investigate instability")

    return insights
