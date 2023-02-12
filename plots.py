import matplotlib.pyplot as plt
from gen_functions import abbreviate_number
import plotly.graph_objs as go
import plotly.express as px

def bar_plot_horizontal_indicator(number_of_bars: int = 2, bars_values : list = [None, None], bars_labels : list = [None, None], color = "blue", use_labels = True): 
    """
    This function generates a horizontal bar plot without borders, axis
    
    Parameters
    ----------
    number of bars : int
        Number of horizontal bars
    bars_values : float
        The value of the bars to being produced
    bars_labels : str
        The label for the bars
    color : str
        Color of the bars
    
    Returns
    -------
    None
    """
    # A space (distance) is establish between the y-axis and the start of the bars, to do dat
    # To make this space always similar the variable distance_axis_bar is created dividing the maximum value of the bars divided by a constant
    # To do so, a white space, overlay the bars with the same colour as the background and add that same distance to the original value of the bars.
    if all(v is None for v in bars_values):
        data = [50]*number_of_bars
        labels = bars_labels
        colors = ["white"]*number_of_bars
    else:
    
        for i, value in enumerate(bars_values):
            if value is None:
                bars_values[i] = 0
        distance_axis_bar = max(bars_values)/6.5
        
        data = [distance_axis_bar]*2*number_of_bars
        for i in range(number_of_bars):
            data[i] = data[i] + bars_values[i] 
        labels = bars_labels*2
        colors = [color]*number_of_bars + ["white"]*number_of_bars
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(3, 1))
    bars = ax.barh(labels, data, height=0.8, color = colors)
    # Add text to each bar, depending on the size of the bar the value will be displayed inside or outside the bar
    if all(v is None for v in bars_values):
        for bar in bars[:number_of_bars]:
            ax.text(50/8, bar.get_y() + bar.get_height()/2, "0 €", ha='left', va='center', color='black')
    else:
        for bar in bars[:number_of_bars]:
            width = bar.get_width() - distance_axis_bar
            value = f'{abbreviate_number(width,0)} €'
            if width <= (max(data)-distance_axis_bar)/3:
                ax.text(width + distance_axis_bar + 25, bar.get_y() + bar.get_height()/2, value, ha='left', va='center', color='black')
            else:
                ax.text(width + distance_axis_bar, bar.get_y() + bar.get_height()/2, value, ha='right', va='center', color='white')

    # Remove the x-axis and y-axis labels
    ax.set_xlabel('')
    ax.set_ylabel('')

    # Configure ticks and delete borders
    ax.set_xticks([])
    ax.tick_params(length=0, labelsize = 10)
    if not use_labels:
        ax.tick_params(colors = "white")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    return fig

def kpi_single_indicator_comparison(kpi_value : float, 
                                    comparison_value : float, 
                                    kpi_label : str, 
                                    comparison_label : str, 
                                    title : str, 
                                    green_for_up : bool = True,
                                    comparison_type : str = "value",
                                    use_labels = True,
                                    background_color = "#ffffff"):
    """
    This function generates a KPI comparison plot using matplotlib.
    
    Parameters
    ----------
    kpi_value : float
        The value of the KPI.
    comparison_value : float
        The value to compare with the KPI.
    kpi_label : str
        The label for the KPI value.
    comparison_label : str
        The label for the comparison value.
    title : str
        The title of the plot.
    green_for_up : bool, optional
        Whether to use green for an increase in the comparison value (default is True).
    
    Returns
    -------
    None
    """
    # Safe values and labels in list. First element is related to compare, second the main KPI and last one is for the title    
    
    if comparison_value is None and kpi_value is None:
        bar_values = [0,1,0]
        real_values = [0,0,0]
    elif comparison_value is None and kpi_value is not None:
        bar_values = [0, kpi_value, 0]
        real_values = [0, kpi_value, 0]
    elif comparison_value is not None and kpi_value is None:
        bar_values = [0, abs(comparison_value), 0]
        real_values = [abs(comparison_value), 0, 0]
        comparison_symbol = "%"
    else:
        bar_values = [0, kpi_value, 0]
        if comparison_type == "percent":
            real_values = [abs((kpi_value - comparison_value)/comparison_value)*100, kpi_value, 0]
            comparison_symbol = "%"
        else: 
            real_values = [abs(kpi_value-comparison_value), kpi_value, 0]
            comparison_symbol = "€"
        
    labels = [comparison_label, kpi_label, '']
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(3, 1))
    height = 0.3
    height_text = 0.7
    # All bars are white, because we are only intered in the values not the bars
    bars = ax.barh(labels, bar_values, height=height, color = [background_color])

    kpi = bars[1]
    comparison = bars[0]
    main = bars[2]

    # Set colors depending on whether the comparison value is positive or negative
    downside_color = "#B71C1C"
    upside_color = "#388E3C"

    if not green_for_up:
        downside_color = "#388E3C"
        upside_color = "#B71C1C"

    # Add text
    ax.text(kpi.get_width()/8, main.get_y(), title, ha='left', va='center', color='grey', fontsize = 11)
    if comparison_value is None and kpi_value is None:
        ax.text(kpi.get_width()/8, kpi.get_y() + height_text/10, "0 €", ha='left', va='center', color='black', fontsize = 24)
        ax.text(kpi.get_width()/8, comparison.get_y()+height_text/5, "Sin datos", ha='left', va='center', color='grey', fontsize = 11)
    elif comparison_value is None and kpi_value is not None:
        ax.text(kpi.get_width()/8, kpi.get_y() + height_text/10, f"{abbreviate_number(real_values[1], 1).replace('-','')} €", ha='left', va='center', color='black', fontsize = 24)
        ax.text(kpi.get_width()/8, comparison.get_y()+height_text/5, "Sin datos", ha='left', va='center', color='grey', fontsize = 11)
    elif comparison_value is not None and kpi_value is None:
        ax.text(kpi.get_width()/8, kpi.get_y() + height_text/10, "0 €", ha='left', va='center', color='black', fontsize = 24)
        ax.text(kpi.get_width()/8, comparison.get_y()+height_text/5, f"↡{abbreviate_number(comparison_value, 1).replace('-','')} €", ha='left', va='center', color=downside_color, fontsize = 11)
    else:
        ax.text(kpi.get_width()/8, kpi.get_y() + height_text/10, f"{abbreviate_number(real_values[1], 1).replace('-','')}€ ", ha='left', va='center', color='black', fontsize = 24)
        if (kpi_value - comparison_value) >= 0:
            ax.text(kpi.get_width()/8, comparison.get_y()+height_text/5, f"↟{abbreviate_number(real_values[0], 1).replace('-','')}{comparison_symbol}", ha='left', va='center', color=upside_color, fontsize = 11)
        else:
            ax.text(kpi.get_width()/8, comparison.get_y()+height_text/5, f"↡{abbreviate_number(real_values[0], 1).replace('-','')}{comparison_symbol}", ha='left', va='center', color=downside_color, fontsize = 11)
    # Remove the x-axis and y-axis labels
    ax.set_xlabel('')
    ax.set_ylabel('')    
    
    # Configure ticks and delete borders
    ax.set_xticks([])
    ax.tick_params(length=0, labelsize = 10)
    ax.spines['top'].set_visible(False)
    if not use_labels:
        ax.tick_params(colors = "white")
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    ax.set_facecolor(background_color)
    fig.set_facecolor(background_color)
    
    fig.set_linewidth(2)

    return fig

def kpi_double_indicator_comparison(kpi_value : float, 
                                    comparison_value_1 : float, 
                                    comparison_value_2 : float,
                                    kpi_label : str, 
                                    comparison_label : str, 
                                    title : str, 
                                    green_for_up : bool = True,
                                    use_labels = True,
                                    background_color = "#ffffff"):
    """
    This function generates a KPI comparison plot using matplotlib.
    
    Parameters
    ----------
    kpi_value : float
        The value of the KPI.
    comparison_value : float
        The value to compare with the KPI.
    kpi_label : str
        The label for the KPI value.
    comparison_label : str
        The label for the comparison value.
    title : str
        The title of the plot.
    green_for_up : bool, optional
        Whether to use green for an increase in the comparison value (default is True).
    
    Returns
    -------
    None
    """
    # Safe values and labels in list. First element is related to compare, second the main KPI and last one is for the title    
    
    if comparison_value_1 is None and comparison_value_2 is None and kpi_value is None:
        bar_values = [0,1,0]
        real_values = [0,0,0,0]
    elif comparison_value_1 is None and comparison_value_2 is None and kpi_value is not None:
        bar_values = [0, abs(kpi_value), 0]
        real_values = [0,0, kpi_value, 0]
    elif comparison_value_1 is not None and comparison_value_2 is None and kpi_value is None:
        bar_values = [0, abs(comparison_value_1), 0]
        real_values = [abs(comparison_value_1),0, 0, 0]
        comparison_symbol = "%"
    elif comparison_value_1 is None and comparison_value_2 is not None and kpi_value is None:
        bar_values = [0, abs(comparison_value_2), 0]
        real_values = [0,abs(comparison_value_2), 0, 0]
        comparison_symbol = "%"
    elif comparison_value_1 is not None and comparison_value_2 is not None and kpi_value is None:
        bar_values = [0, abs(comparison_value_1), 0]
        real_values = [abs(comparison_value_1),abs(comparison_value_2), 0, 0]
        comparison_symbol = "%"
    elif comparison_value_1 is not None and comparison_value_2 is None and kpi_value is not None:
        bar_values = [0, abs(kpi_value), 0]
        real_values = [abs((kpi_value - comparison_value_1)/kpi_value)*100,0, kpi_value, 0]
        comparison_symbol = "%"
    elif comparison_value_1 is None and comparison_value_2 is not None and kpi_value is not None:
        bar_values = [0, abs(kpi_value), 0]
        real_values = [0,abs((kpi_value - comparison_value_2)/kpi_value)*100, kpi_value, 0]
        comparison_symbol = "%"
    else:
        bar_values = [0, abs(kpi_value), 0]
        real_values = [abs((kpi_value - comparison_value_1)/kpi_value)*100, abs((kpi_value - comparison_value_2)/comparison_value_2)*100, kpi_value, 0]
        comparison_symbol = "%"
        
    labels = [comparison_label, kpi_label, '']
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(3, 1))
    height = 0.3
    height_text = 0.7
    # All bars are white, because we are only intered in the values not the bars
    bars = ax.barh(labels, bar_values, height=height, color = [background_color])

    kpi = bars[1]
    comparison = bars[0]
    main = bars[2]

    # Set colors depending on whether the comparison value is positive or negative
    downside_color = "#B71C1C"
    upside_color = "#388E3C"

    if not green_for_up:
        downside_color = "#388E3C"
        upside_color = "#B71C1C"

    # Add text
    ax.text(kpi.get_width()/8, main.get_y(), title, ha='left', va='center', color='grey', fontsize = 11)
    if comparison_value_1 is None and comparison_value_2 is None and kpi_value is None:
        ax.text(kpi.get_width()/8, kpi.get_y() + height_text/10, "0 €", ha='left', va='center', color='black', fontsize = 24)
        ax.text(kpi.get_width()/8, comparison.get_y()+height_text/5, "Sin datos", ha='left', va='center', color='grey', fontsize = 11)
    elif comparison_value_1 is None and comparison_value_2 is None and kpi_value is not None:
        ax.text(kpi.get_width()/8, kpi.get_y() + height_text/10, f"{abbreviate_number(real_values[2], 1)} €", ha='left', va='center', color='black', fontsize = 24)
        ax.text(kpi.get_width()/8, comparison.get_y()+height_text/5, "Sin datos", ha='left', va='center', color='grey', fontsize = 11)
    elif comparison_value_1 is not None and comparison_value_2 is None and kpi_value is None:
        ax.text(kpi.get_width()/8, kpi.get_y() + height_text/10, "0 €", ha='left', va='center', color='black', fontsize = 24)
        ax.text(kpi.get_width()/8, comparison.get_y()+height_text/5, f"↡{abbreviate_number(comparison_value_1, 1, small_number=1000).replace('-','')} €", ha='left', va='center', color=downside_color, fontsize = 11)
        ax.text(kpi.get_width()/8 + kpi.get_width()/3, comparison.get_y()+height_text/5, "Sin datos", ha='left', va='center', color='grey', fontsize = 11)
    elif comparison_value_1 is None and comparison_value_2 is not None and kpi_value is None:
        ax.text(kpi.get_width()/8, kpi.get_y() + height_text/10, "0 €", ha='left', va='center', color='black', fontsize = 24)
        ax.text(kpi.get_width()/8, comparison.get_y()+height_text/5, "Sin datos", ha='left', va='center', color='grey', fontsize = 11)
        ax.text(kpi.get_width()/8 + kpi.get_width()/3, comparison.get_y()+height_text/5, f"↡{abbreviate_number(comparison_value_2, 1, small_number=1000).replace('-','')} €", ha='left', va='center', color=downside_color, fontsize = 11)
    elif comparison_value_1 is not None and comparison_value_2 is not None and kpi_value is None:
        ax.text(kpi.get_width()/8, kpi.get_y() + height_text/10, "0 €", ha='left', va='center', color='black', fontsize = 24)
        ax.text(kpi.get_width()/8, comparison.get_y()+height_text/5, "Sin datos", ha='left', va='center', color='grey', fontsize = 11)
    elif comparison_value_1 is not None and comparison_value_2 is None and kpi_value is not None:
        ax.text(kpi.get_width()/8, kpi.get_y() + height_text/10, f"{abbreviate_number(real_values[2], 1)} €", ha='left', va='center', color='black', fontsize = 24)
        if (kpi_value - comparison_value_1) >= 0:
            ax.text(kpi.get_width()/8, comparison.get_y()+height_text/5, f"↟{abbreviate_number(real_values[0], 1).replace('-','')}{comparison_symbol}", ha='left', va='center', color=upside_color, fontsize = 11)
        else:
            ax.text(kpi.get_width()/8, comparison.get_y()+height_text/5, f"↡{abbreviate_number(real_values[0], 1).replace('-','')}{comparison_symbol}", ha='left', va='center', color=downside_color, fontsize = 11)
        ax.text(kpi.get_width()/8 + kpi.get_width()/3, comparison.get_y()+height_text/5, "Sin datos", ha='left', va='center', color='grey', fontsize = 11)
    elif comparison_value_1 is None and comparison_value_2 is not None and kpi_value is not None:
        ax.text(kpi.get_width()/8, kpi.get_y() + height_text/10, f"{abbreviate_number(real_values[2], 1)} €", ha='left', va='center', color='black', fontsize = 24)
        ax.text(kpi.get_width()/8, comparison.get_y()+height_text/5, "Sin datos", ha='left', va='center', color='grey', fontsize = 11)
        if (kpi_value - comparison_value_2) >= 0:
            ax.text(kpi.get_width()/8 + kpi.get_width()/3, comparison.get_y()+height_text/5, f"↟{abbreviate_number(real_values[1], 1).replace('-','')}{comparison_symbol}", ha='left', va='center', color=upside_color, fontsize = 11)
        else:
            ax.text(kpi.get_width()/8 + kpi.get_width()/3, comparison.get_y()+height_text/5, f"↡{abbreviate_number(real_values[1], 1).replace('-','')}{comparison_symbol}", ha='left', va='center', color=downside_color, fontsize = 11)
    else:
        ax.text(kpi.get_width()/8, kpi.get_y() + height_text/10, f"{abbreviate_number(real_values[2], 1)}€ ", ha='left', va='center', color='black', fontsize = 24)
        if (kpi_value - comparison_value_1) >= 0:
            ax.text(kpi.get_width()/8, comparison.get_y()+height_text/5, f"↟{abbreviate_number(real_values[0], 1).replace('-','')}{comparison_symbol}", ha='left', va='center', color=upside_color, fontsize = 11)
        else:
            ax.text(kpi.get_width()/8, comparison.get_y()+height_text/5, f"↡{abbreviate_number(real_values[0], 1).replace('-','')}{comparison_symbol}", ha='left', va='center', color=downside_color, fontsize = 11)
        if (kpi_value - comparison_value_2) >= 0:
            ax.text(kpi.get_width()/8 + kpi.get_width()/3, comparison.get_y()+height_text/5, f"↟{abbreviate_number(real_values[1], 1).replace('-','')}{comparison_symbol}", ha='left', va='center', color=upside_color, fontsize = 11)
        else:
            ax.text(kpi.get_width()/8 + kpi.get_width()/3, comparison.get_y()+height_text/5, f"↡{abbreviate_number(real_values[1], 1).replace('-','')}{comparison_symbol}", ha='left', va='center', color=downside_color, fontsize = 11)
    # Remove the x-axis and y-axis labels
    ax.set_xlabel('')
    ax.set_ylabel('')    
    
    # Configure ticks and delete borders
    ax.set_xticks([])
    ax.tick_params(length=0, labelsize = 10)
    ax.spines['top'].set_visible(False)
    if not use_labels:
        ax.tick_params(colors = "white")
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    ax.set_facecolor(background_color)
    fig.set_facecolor(background_color)
    
    fig.set_linewidth(2)

    return fig

def sankey_movements_plot(incomes : list, incomes_values, expenses : list, expenses_values, safes : list = ["Efectivo"], safes_percent : list = [1]):
    
    safes_total = sum(incomes_values) - sum(expenses_values)
    safes_values = [i*safes_total for i in safes_percent]
    safes_difference = sum(safes_values) - safes_total

    
    if safes_total > 0 and safes_difference == 0:
        labels = incomes + ["Ingresos", "Ahorro", "Gastos"] + safes + expenses 
        x_pos = [0]*len(incomes) + [0.2, 0.7, 0.45] + [1]*len(safes) + [0.65]*len(expenses) 
        y_pos = [0.5]*len(incomes) + [0.5, 0.9, 0.3] + [0.8]*len(safes) + [0.1]*len(expenses) 
        source = [i for i in range(len(incomes))] + [len(incomes),len(incomes)] + [len(incomes)+1]*len(safes) + [len(incomes)+2]*len(expenses) 
        target = [len(incomes)]*len(incomes) + [len(incomes)+1,len(incomes)+2] + [len(incomes)+(i+3) for i in range(len(safes))] + [len(incomes)+len(safes)+3+i for i in range(len(expenses))] 
        values = incomes_values + [sum(safes_values)] + [sum(expenses_values)] + safes_values + expenses_values

    elif safes_total > 0 and safes_difference > 0:
        labels = incomes + ["Ingresos", "Ahorros", "Ahorro", "Gastos"] + safes + expenses
        x_pos = [0]*len(incomes) + [0.2, 0.2, 0.7, 0.45] + [1]*len(safes) + [0.65]*len(expenses)
        y_pos = [0.5]*len(incomes) + [0.5, 0.5, 0.9, 0.3] + [0.8]*len(safes) + [0.1]*len(expenses)
        source = [i for i in range(len(incomes))] + [len(incomes)+1,len(incomes), len(incomes)] + [len(incomes)+2]*len(safes) + [len(incomes)+3]*len(expenses)
        target = [len(incomes)]*len(incomes) + [len(incomes)+2,len(incomes)+2, len(incomes)+3] + [len(incomes)+(i+4) for i in range(len(safes))] + [len(incomes)+len(safes)+4+i for i in range(len(expenses))] 
        values = incomes_values + [safes_difference] + [safes_total] + [sum(expenses_values)] + safes_values + expenses_values
    
    elif safes_total == 0:
        labels = incomes + ["Ingresos", "Gastos"] + expenses 
        x_pos = [0]*len(incomes) + [0.3, 0.6] + [1]*len(expenses) 
        y_pos = [0.5]*len(incomes) + [0.5, 0.5] + [0]*len(expenses) 
        source = [i for i in range(len(incomes))] + [len(incomes)] + [len(incomes)+1]*len(expenses) 
        target = [len(incomes)]*len(incomes) + [len(incomes)+1] + [len(incomes)+(i+2) for i in range(len(expenses))]
        values = incomes_values +  [sum(incomes_values)] + expenses_values
    
    elif safes_total < 0:
        labels = incomes + ["Ingresos", "Ahorros/Deuda","Gastos"] + expenses 
        x_pos = [0]*len(incomes) + [0.3, 0.3, 0.6] + [1]*len(expenses) 
        y_pos = [0.5]*len(incomes) + [0.3, 0.8, 0.5] + [0]*len(expenses) 
        source = [i for i in range(len(incomes))] + [len(incomes), len(incomes)+1] + [len(incomes)+2]*len(expenses) 
        target = [len(incomes)]*len(incomes) + [len(incomes)+2,len(incomes)+2] + [len(incomes)+(i+3) for i in range(len(expenses))]
        values = incomes_values +  [sum(incomes_values), abs(safes_total)] + expenses_values

    fig = go.Figure(go.Sankey(
            arrangement = "snap",
            node = {
                "label": labels,
                "x": x_pos,
                "y": y_pos,
                'pad':10},  # 10 Pixels
            link = {
                "source": source,
                "target": target,
                "value": values}))
    return fig

def bar_plot_unifiedhover(df, x, y, x_label, y_label, title:str = None,
                y_ticksuffix="", height=300, series:str = None, text_auto = False):
    """
    series is to add more columns as series
    """
    if series:
        fig = px.bar(df, x=x, y=y, color=series, barmode="group", text_auto=text_auto,
        labels={
            x: x_label,
            y: y_label
            },

            hover_data={
                x:False,
                y:':.1f'
            },
        height=height
        )
    else:
        fig = px.bar(df, x=x, y=y, text_auto=text_auto, labels={
                x: x_label,
                y: y_label
                },
                hover_data={
                    x:False,
                    y:':.1f'
                },
            height=height
            )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=title
        )
    fig.update_layout(hovermode="x unified", hoverlabel=dict(bgcolor='rgba(255,255,255,0.95)'))

    fig.update_layout(
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            title=None,
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
                ),
            ),
        yaxis=dict(
            showline=True,
            showgrid=True,
            ticksuffix = y_ticksuffix,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            title=None,
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
                ),
            ),
        autosize=False,
        margin=dict(
            autoexpand=False,
            l=50,
            r=20,
            t=40,
            ),
        )
    return fig

def line_plot_unifiedhover(df, x, y, x_label, y_label, title:str = None,
                y_ticksuffix="", height=300, series=None, text=None, series_label=None,
                color_discrete_map={}):
    fig = px.line(df, x=x, y=y, color=series, text=text, labels={
            x: x_label,
            series: series_label,
            y: y_label
            },
            markers= True,
            hover_data={
                x:False,
                y:':.1f'
            },
            color_discrete_map=color_discrete_map,
            height=height
        )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=title
        )
    fig.update_layout(hovermode="x unified", hoverlabel=dict(bgcolor='rgba(255,255,255,0.95)'))

    fig.update_layout(
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            title=None,
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
                ),
            ),
        yaxis=dict(
            showline=True,
            showgrid=True,
            ticksuffix = y_ticksuffix,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            title=None,
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
                ),
            ),
        autosize=False,
        margin=dict(
            autoexpand=False,
            l=50,
            r=20,
            t=40,
            ),
        )
    return fig

def line_bar_plot_unifiedhover(df, x, y_bars, y_line, x_label, y_bars_label, y_line_label, color_bars, color_line,
                title:str = None, y_ticksuffix="", height=300):
    fig = px.line(df, x=x, y=y_line,
        labels={
            x: x_label,
            y_line: y_line_label
            },
            markers= True,
            hover_data={
                x:False,
                y_line:':.1f'
            },
        height=height
        ).update_traces(line_color=color_line, name=y_line_label)
    
    for i,y_bar in enumerate(y_bars):                
        fig.add_traces(
            px.bar(df, x=x, y=y_bar, barmode="group", 
        labels={
            x: x_label,
            y_bar: y_bars_label[i]
            },
            hover_data={
                x:False,
                y_bar:':.1f'
            },
        height=height
        ).update_traces(marker_color = color_bars[i], name=y_bars_label[i]).data
        )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=title,
        showlegend=True
        )
    fig.update_layout(hovermode="x unified", hoverlabel=dict(bgcolor='rgba(255,255,255,0.95)'))

    fig.update_layout(
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            title=None,
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
                ),
            ),
        yaxis=dict(
            showline=True,
            showgrid=True,
            ticksuffix = y_ticksuffix,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            title=None,
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
                ),
            ),
        autosize=False,
        margin=dict(
            autoexpand=False,
            l=50,
            r=20,
            t=40,
            ),
        )
    return fig