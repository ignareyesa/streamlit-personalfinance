posneg_cellstyle = """
function(params) {
    if (params.value < 0) {
        return {
            'color': 'red'
        }
    } else {
        return {
            'color': 'green'
        }
    }
};
"""

date_cellstyle = """
function(params) {
    var date = new Date(params.value);
    console.log(date);

    var options = {
        year: "numeric",
        month: "long",
        day: "numeric"
    };

    return date.toLocaleDateString("es-ES", options);
};
"""
euro_cellstyle = """
function(params) {
    return params.value.toFixed(2) + ' €';
}
"""