import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
from dash_table import DataTable

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

########### Set up the layout
import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
from dash_table import DataTable

from random import sample
edge=lambda n, m: n*m**n

def genPayoffs(numPlayers, numStrats):
    edges=edge(numPlayers, numStrats)
    return sample(range(edges), edges)

toList = lambda string: list(map(int, string.split()))

group=lambda lis, size: [lis[i*size: (i+1)*size] for i in range(len(lis)//size)]

def shape(payoffs, numPlayers, numStrats):
    grouped=group(payoffs, numPlayers)
    for i in range(numPlayers-1):
        grouped=group(grouped, numStrats)
    return grouped

def toBase(n):
    digits = []
    while n:
        digits.append(int(n % numStrats))
        n //= numStrats
    return (numPlayers-len(digits))*[0]+digits[::-1]

getTensor = lambda lis: {tuple(toBase(i)): x for i, x in enumerate(lis)}

getZeroes=lambda tensor, i: {key: value for key, value in tensor.items() if key[i]==0}

ignore=lambda lis, j: [x for i, x in enumerate(lis) if i!=j]

getSimilar=lambda tensor, cord, i: {key: value for key, value in tensor.items() if ignore(key, i)==ignore(cord, i)}

getMax=lambda similar, ind: sorted(similar.items(), key=lambda x: x[1][ind])[-1][0]

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

def getAllLocals(tensor, numPlayers):
    allLocals=[]
    for i in range(numPlayers):
        zeroes=getZeroes(tensor, i)
        allLocals+=getLocals(tensor, zeroes, i)
    return allLocals

def getFreqs(lis):
    dic={}
    for ele in lis:
        if ele not in dic:
            dic[ele]=1
        else:
            dic[ele]+=1
    return dic

def getAnswers(tensor, freqs):
    cords=[key for key, value in freqs.items() if value==numPlayers]
    return {cord: tensor[cord] for cord in cords}

def compute(grouped):
    tensor=getTensor(grouped)
    allLocals=getAllLocals(tensor, numPlayers)
    freqs=getFreqs(allLocals)
    return getAnswers(tensor, freqs)

def getNameList(solutions):
    nameList=[['', 'Player']]
    for i, solution in enumerate(solutions):
        nameList.append([f'Solution {i}', 'Strategy'])
        nameList.append([f'Solution {i}', 'Payoff'])
    return nameList

def getColumns(solutions):
    nameList=getNameList(solutions)
    return [dict(name=name, id=str(i)) for i, name in enumerate(nameList)]

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
    return getColumns(solutions), getData(solutions)

app.layout = html.Div([
    html.H1('Payoff Matrix Solver'),
    html.H3('This app can solve payoff matrices with any number of players and strategies'),
    
    html.Label('Number of Players: '),
    dcc.Input(id='numPlayers', type='number', value=0),    
    html.Br(),
    
    html.Label('Number of Strategies per Player: '),
    dcc.Input(id='numStrats', type='number', value=0), 
    html.Br(),
    
    html.Div(id='inputs'), 
    html.Br(),
    
    html.Button('Generate Random Payoffs', id='random'), 
    
    html.Label(' or '),  
    
    html.Label('Input Payoffs: '),
    dcc.Input(id='payoffString', value=''),    
    html.Br(),
    
    html.Div(id='payoffs'), 
    html.Br(),
    
    html.Button('Solve', id='solve'), 
    html.Br(), 
    
    html.Div(id='solution'), 
    html.Br(),
    
    DataTable(
        id='table',
        merge_duplicate_headers=True,
        style_header=dict(
            backgroundColor='rgb(230, 230, 230)',
            fontWeight='bold',
        ),
    ),
])

numPlayers, numStrats = 1, 1

@app.callback(
    [
        Output('inputs', 'children'),
    ],
    [
        Input('numPlayers', 'value'),
        Input('numStrats', 'value'),
    ]
)
def storeInputs(p, s):
    global numPlayers, numStrats
    numPlayers, numStrats = p, s
    
    return (
        f'{numPlayers} players, {numStrats} strategies each',
    )

grouped=1

@app.callback(
    [
        Output('payoffs', 'children'),
    ],
    [
        Input('random', 'n_clicks'),
        Input('payoffString', 'value'),
    ]
)
def showPayoffs(clicks, payoffString):  
    if payoffString=='':
        payoffs=genPayoffs(numPlayers, numStrats)
    else:
        payoffs=toList(payoffString)
    
    global grouped
    grouped=group(payoffs, numPlayers)
    
    edges=edge(numPlayers, numStrats)
    if len(payoffs)==edges:
        rtn=str(shape(payoffs, numPlayers, numStrats))
    else:
        rtn=f'Incorrect number of payoffs. Should have {edges}.'
    
    return (
        rtn,
    )

solutions=1

@app.callback(
    [
        Output('solution', 'children'),
        Output('table', 'columns'),
        Output('table', 'data'),
    ],
    [
        Input('solve', 'n_clicks'),
    ]
)
def showSolution(clicks):
    global solutions
    solutions=compute(grouped)
    
    string='No Solutions'
    columns, data = [], []
    
    if len(solutions)>0:
        string=str(solutions)        
        columns, data = getTable(solutions)
    
    return (
        string,
        columns,
        data,
    )

if __name__ == '__main__':
    app.run_server()
