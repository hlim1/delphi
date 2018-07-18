import pandas as pd
from .AnalysisGraph import AnalysisGraph
from datetime import datetime
from typing import Optional
from .assembly import get_indicator_value, get_data


def parameterize(
    G: AnalysisGraph, time: datetime, data: Optional[pd.DataFrame] = None
) -> AnalysisGraph:
    """ Parameterize the analysis graph.

    Args:
        G
        time
        data
    """

    if data is not None:
        G.data = data
    else:
        if G.data is None:
            G.data = get_data(south_sudan_data)
        else:
            pass

    nodes_with_indicators = [
        n for n in G.nodes(data=True) if n[1]["indicators"] is not None
    ]

    for n in nodes_with_indicators:
        for indicator in n[1]["indicators"]:
            indicator.mean, indicator.unit = get_indicator_value(
                indicator, time, G.data
            )
            indicator.time = time
            if not indicator.mean is None:
                indicator.stdev = 0.1 * abs(indicator.mean)
        n[1]["indicators"] = [
            ind for ind in n[1]["indicators"] if ind.mean is not None
    ]
    return G
