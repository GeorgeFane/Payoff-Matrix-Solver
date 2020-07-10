from dash import Dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output, State
from dash_table import DataTable

import json

from random import sample
edge=lambda n, m: n*m**n

def genPayoffs(numPlayers, numStrats):
    edges=edge(numPlayers, numStrats)
    return sample(range(edges), edges)

toList = lambda string: list(map(int, string.split()))

group=lambda lis, size: [lis[i*size: (i+1)*size] for i in range(len(lis)//size)]

def toBase(n, numPlayers, numStrats):
    digits = []
    while n:
        digits.append(int(n % numStrats))
        n //= numStrats
    return (numPlayers-len(digits))*[0]+digits[::-1]

getTensor = lambda lis, numPlayers, numStrats: {str(toBase(i, numPlayers, numStrats)): x for i, x in enumerate(lis)}

unstringKeys = lambda dic: {tuple(json.loads(key)): value for key, value in dic.items()}

getZeroes=lambda tensor, i: {key: value for key, value in tensor.items() if key[i]==0}

ignore=lambda lis, j: [x for i, x in enumerate(lis) if i!=j]

getSimilar=lambda tensor, cord, i: {key: value for key, value in tensor.items() if ignore(key, i)==ignore(cord, i)}

def getMax(similar, ind):
    maxVal=-1
    cord=1
    
    for key, value in similar.items():
        if value[ind]>maxVal:
            maxVal=value[ind]
            cord=key
            
    return cord

def getLocals(tensor, zeroes, ind):
    localMax=[]
    for key, value in zeroes.items():
        similar=getSimilar(tensor, key, ind)
        localMax.append(getMax(similar, ind))
    return localMax

def getAllLocals(tensor):
    allLocals=[]
    length=len(list(tensor.keys())[0])
    for i in range(length):
        zeroes=getZeroes(tensor, i)
        allLocals+=getLocals(tensor, zeroes, i)
    return allLocals

getFreqs=lambda lis: {key: lis.count(key) for key in set(lis)}

getCords = lambda freqs: [key for key, value in freqs.items() if value==len(key)]

getPairs = lambda tensor, cords: {key: tensor[key] for key in cords}

def compute(tensor):
    allLocals=getAllLocals(tensor)
    freqs=getFreqs(allLocals)
    cords=getCords(freqs)
    return getPairs(tensor, cords)

#DIVIDER BETWEEN BACKEND AND FRONTEND

def getNames(solutions):
    names=[['', 'Player']]
    for i, solution in enumerate(solutions):
        names.append([f'Solution {i}', 'Strategy'])
        names.append([f'Solution {i}', 'Payoff'])
    return names

def getColumns(solutions):
    names=getNames(solutions)
    return [dict(name=name, id=str(i)) for i, name in enumerate(names)]

def flatten(solutions):
    grid=[]
    for key, value in solutions.items():
        grid.append(key)
        grid.append(value)
    return grid

transpose=lambda matrix: [[row[j] for row in matrix] for j in range(len(matrix[0]))]

addPlayer=lambda matrix: [[i]+row for i, row in enumerate(matrix)]

def getData(solutions):
    flat=flatten(solutions)
    tposed=transpose(flat)
    values=addPlayer(tposed)
    
    return [{str(i): x for i, x in enumerate(row)} for row in values]

def getTable(solutions):
    if len(solutions)>0:
        return getColumns(solutions), getData(solutions)
    else:
        return [dict(name='No Solutions', id='0')], []

app = Dash(__name__)
server = app.server

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = JupyterDash(__name__)#, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('Payoff Matrix Solver'),
    html.H3('This app can solve payoff matrices with any number of players and strategies'),
    
    html.Div([
        html.Label('Number of Players: '),
        dcc.Input(id='numPlayers', type='number'),    
        html.Br(),

        html.Label('Number of Strategies: '),
        dcc.Input(id='numStrats', type='number'), 

        html.Div(id='inputs', style={'display': 'none'}), 
        html.Br(),
        html.Br(),

        html.Button('Generate Random Payoffs', id='random'), 
        html.Br(),

        html.Label('or Input Payoffs: '),
        dcc.Input(id='payoffString', value=''),    
        html.Br(),
        html.Br(),

        html.Div(id='payoffs'),  
        html.Br(),
    ], 
        style=dict(
            width='49%',
            display='inline-block',
        )
    ),

    html.Div([
        DataTable(
            id='table',
            merge_duplicate_headers=True,
            style_header=dict(
                backgroundColor='rgb(230, 230, 230)',
                fontWeight='bold',
                textAlign='left',
            ),
        ), 
    ], 
        style=dict(
            width='49%',
            display='inline-block',
            verticalAlign='top',
        )
    ),
])

@app.callback(
    [
        Output('inputs', 'children'),
    ],
    [
        Input('numPlayers', 'value'),
        Input('numStrats', 'value'),
    ]
)
def storeInputs(numPlayers, numStrats):
    return (
        json.dumps([numPlayers, numStrats]),
    )

@app.callback(
    [
        Output('payoffs', 'children'),
    ],
    [
        Input('random', 'n_clicks'),
        Input('payoffString', 'value'),
    ],
    [        
        State('inputs', 'children'),
    ],
)
def showPayoffs(clicks, payoffString, inputs):  
    numPlayers, numStrats = json.loads(inputs)
    
    if payoffString=='':
        payoffs=genPayoffs(numPlayers, numStrats)
    else:
        payoffs=toList(payoffString)
    
    edges=edge(numPlayers, numStrats)
    if len(payoffs)==edges:
        grouped=group(payoffs, numPlayers)
        tensor=getTensor(grouped, numPlayers, numStrats)
        rtn=json.dumps(tensor)
    else:
        rtn=f'Incorrect number of payoffs. Should have {edges}.'
        
    return (
        rtn,
    )

@app.callback(
    [
        Output('table', 'columns'),
        Output('table', 'data'),
    ],
    [
        Input('payoffs', 'children'),
    ],
)
def showSolution(payoffs):
    tensor=unstringKeys(json.loads(payoffs))
    solutions=compute(tensor)
    
    columns, data = getTable(solutions)
    
    return (
        columns,
        data,
    )
	
if __name__ == '__main__':
    app.run_server()
