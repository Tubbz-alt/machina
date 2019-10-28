import ipdb
import altair as alt


class Bar:
    def __init__(self, xaxis=None, yaxis=None, negative=True, size=20, labels=True):
        self.size = size
        self.xaxis = xaxis
        self.yaxis = yaxis
        self.labels = labels
        self.negative = negative

    def plot(self, data):
        rounded = []
        names = []
        
        for n, v in data:
            rounded.append(round(v, 2))
            names.append(n)

        values = sorted([{'feature': k, 
                          'weight': v if self.negative else abs(v), 
                          'class_': 'pos' if v >= 0 else 'neg' } for k,v in zip(names, rounded)], 
                        key=lambda x: abs(x['weight']), reverse=True)

        _data = alt.Data(values=values)

        base = alt.Chart(_data).encode(
            alt.Y("feature:O", 
                  axis=alt.Axis(title=self.yaxis),
                  scale=alt.Scale(rangeStep=self.size + 10),
                  sort=None
            )
        )

        bars = base.mark_bar(
            size=self.size
        ).encode(
            alt.X('weight:Q', axis=alt.Axis(title=self.xaxis) if self.xaxis else None),
            color=alt.condition(
                alt.datum.class_ == 'pos',
                alt.value( "rgb(135, 188, 85)"),  # The positive color 
                alt.value("rgb(123, 72, 148)")  # The negative color
            )
        )

        if self.labels:
            text = base.mark_text(
                align='left',
                baseline='middle',
                dx=5,
                fontSize=12
            )

            right = text.transform_filter(alt.datum.weight > 0).encode(
                alt.X('weight:Q', axis=alt.Axis(title=self.xaxis)),
                text='weight:Q',
            )

            left = text.transform_filter(alt.datum.weight < 0).transform_calculate(
                x='0',
            ).encode(
                alt.X('x:Q', axis=alt.Axis(title=self.xaxis)),
                text='weight:Q',
            )

            chart = bars + right + left
        else:
            chart = bars
        
        chart = chart.configure_view(
            strokeWidth=0
        ).configure_axis(
            labelFontSize=12,
        )

        return chart