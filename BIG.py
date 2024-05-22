import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend (non-interactive, suitable for web applications)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import Flask, request, send_file, render_template_string
from io import BytesIO


app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                margin: 0;
                height: 100vh;
                background-color: #f9f9f9;
            }
            h1 {
                color: #333;
                font-weight: bold;
            }
            h2 {
                color: #666;
                font-size: 16px;
                margin-bottom: 20px;
            }
            form {
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            label {
                font-weight: bold;
                display: block;
                margin-bottom: 10px;
                text-align: center;
            }
            table {
                width: 80%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            th, td {
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            input[type="text"] {
                width: 100%;
                padding: 6px;
                box-sizing: border-box;
            }
            .button-container {
                text-align: center;
                width: 100%;
            }
            input[type="button"], input[type="submit"] {
                padding: 10px 20px;
                margin-top: 10px;
                background-color: #4CAF50;
                color: white;
                border: none;
                cursor: pointer;
            }
            input[type="button"] {
                background-color: #cccccc;
                color: black;
            }
            input[type="button"]:hover {
                background-color: #999999;
            }
            input[type="submit"]:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <h2>Created for NaturallyContained 🌱 by Chetan Sidhu:</h2>
        <h1>Willingness To Pay Plotter 💰</h1>
        <form action="/plot" method="post" onsubmit="return validateForm()">
            <label for="price">Product Price ($):</label>
            <input type="text" id="price" name="price">
            <br><br>
            <table id="dataTable">
                <tr>
                    <th>Soil Producer Name</th>
                    <th>Willingness to Pay ($)</th>
                </tr>
                <tr>
                    <td><input type="text" name="payLabels[0]"></td>
                    <td><input type="text" name="pay[0]"></td>
                </tr>
                <tr>
                    <td><input type="text" name="payLabels[1]"></td>
                    <td><input type="text" name="pay[1]"></td>
                </tr>
                <!-- Add more rows as needed -->
            </table>
            <div class="button-container">
                <input type="button" value="Add Row" onclick="addRow('dataTable')">
            </div>
            <input type="submit" value="Generate Plot">
        </form>
        <script>
            function addRow(tableID) {
                var table = document.getElementById(tableID);
                var rowCount = table.rows.length;
                var newRow = table.insertRow(rowCount);
                
                var cell1 = newRow.insertCell(0);
                var cell2 = newRow.insertCell(1);

                cell1.innerHTML = '<input type="text" name="payLabels[' + (rowCount - 1) + ']">';
                cell2.innerHTML = '<input type="text" name="pay[' + (rowCount - 1) + ']">';
            }

            function validateForm() {
                var price = document.getElementById('price').value;
                var table = document.getElementById('dataTable');
                var rowCount = table.rows.length;

                if (!isValidNumber(price)) {
                    alert('Please enter a valid number for the Product Price.');
                    return false;
                }

                for (var i = 1; i < rowCount; i++) { // start from 1 to skip header row
                    var payLabel = table.rows[i].cells[0].getElementsByTagName('input')[0].value;
                    var pay = table.rows[i].cells[1].getElementsByTagName('input')[0].value;

                    if (payLabel.trim() === '') {
                        alert('Please enter valid names for all "Soil Producer Name" fields.');
                        return false;
                    }

                    if (!isValidNumber(pay)) {
                        alert('Please enter a valid number for all "Willingness to Pay" fields.');
                        return false;
                    }
                }

                return true;
            }

            function isValidNumber(value) {
                return !isNaN(value) && value.trim() !== '';
            }
        </script>
    </body>
    </html>
    '''

@app.route('/plot', methods=['POST'])
def plot_png():
    price = list(map(float, request.form['price'].split(',')))
    gridChoice = 1

    # Retrieve values for pay and payLabels from the form data
    pay_values = []
    payLabels_values = []
    for key in request.form:
        if key.startswith('pay['):
            pay_values.append(float(request.form[key]))
        elif key.startswith('payLabels['):
            payLabels_values.append(request.form[key])

    fig = create_plot(price, pay_values, payLabels_values, gridChoice)
    output = BytesIO()
    fig.savefig(output, format='png')
    output.seek(0)
    return send_file(output, mimetype='image/png')


def create_plot(price, payArray, payLabelsArray, gridChoice):
    price = pd.Series(price)
    fig = WTP(price, payArray, payLabelsArray, gridChoice)
    return fig

def WTP(price, payArray, payLabelsArray, gridChoice):
    fig, ax = plt.subplots()

    # sets the gridlines to the payArray
    gridLines = payArray
    # finds the number of producers for the graph
    length = len(payArray) + 1

    # adds all necessary points to the payArray
    adjustedPayArray = []
    for i in payArray:
        adjustedPayArray.append(i)
        adjustedPayArray.append(i)
    adjustedPayArray.append(0)
    payArray = adjustedPayArray

    # Draw a horizontal line at the first price point
    ax.axhline(y=price.iloc[0], color='g', linestyle='-') 

    # creates all the points for the labels and adds them to the payLabelsArray
    adjustedPayArrayLabels = []
    for i in payLabelsArray:
        adjustedPayArrayLabels.append(i)
        adjustedPayArrayLabels.append(i)
    adjustedPayArrayLabels.pop(0)
    payLabelsArray = adjustedPayArrayLabels
    payLabelsArray.append("")
    payLabelsArray.append("")

    # generates the x values that the labels will be mapped to
    xValues = []
    for i in range(length):
        xValues.append(i)
        xValues.append(i)
    xValues.pop(0)

    # plots array into a line graph
    x = np.array(xValues)
    y = np.array(payArray)
    my_xticks = payLabelsArray
    ax.set_xticks(x)
    ax.set_xticklabels(my_xticks)
    ax.plot(x, y, color="brown")
    
    # adds gridlines to the graph based on gridChoice
    if gridChoice == 1:
        ax.grid(True)
        gridLines = list(gridLines)
        gridLines.pop(0)
        xAxis = 1
        for i in gridLines:
            y1 = np.array([i, 0])
            x1 = np.array([xAxis, xAxis])
            ax.plot(x1, y1, color="brown", linestyle="dashed")
            xAxis = xAxis + 1
        
    # sets 0,0 at the origin
    ax.set_xlim([0, max(x)+0.5])
    ax.set_ylim([0, max(y)+0.5])

    # labels the x and y axis
    ax.set_title("Willingness To Pay Model", color='black')
    ax.set_xlabel("Soil Producers", color='brown')
    ax.set_ylabel("Price", color='green')

    return fig

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
