# -*- coding: utf-8 -*-
from __future__ import print_function
import sys, os, datetime, argparse, time
import numpy as np
from random import randint

parser = argparse.ArgumentParser()
parser.add_argument('-i', dest='inputMatrix', help='Nome do arquivo de entrada com a matriz de adjacência')
parser.add_argument('-o', dest='outputFile', help='Nome para o arquivo de de configuração para o GraphViz')
parser.add_argument('-t', dest='timeInterval', type=int, help='Define o intervalo de tempo em segundos para geração e atualização de rotas')
parser.add_argument('-n', dest='nIterations', type=int, help='Define a quantidade de iterações com -t segundos entre cada uma')

args = parser.parse_args()

#Exibe a ajuda se faltar algum argumento
if (len(sys.argv)) != 9:
    parser.print_help()
    quit()

input_file = open(args.inputMatrix, "r")

file_contents = input_file.readlines()
mDim = int(file_contents[0][0])
adj_matrix = np.zeros( (mDim,mDim), dtype=np.int32 )

#Retira os espaços em branco entre os dados no arquivo de entrada
for line in range(1,len(file_contents)):
    file_contents[line] = file_contents[line].replace(" ", "")

#Carrega os dados do arquivo para a matriz
for line in range(1,mDim + 1):
    for column in range(mDim):
        adj_matrix[line - 1][column] = file_contents[line][column]

#Atribui um peso pseudo-aleatório para as arestas válidas do grafo
def initWeights(adj_matrix):
    for line in range(mDim):
        for column in range(mDim):
            if adj_matrix[line][column] != 0:
                adj_matrix[line][column] = randint(5,20)

#Atualiza os valores das arestas de forma pseudo-aleatória
def updateWeights(adj_matrix):
    for line in range(mDim):
        for column in range(mDim):
            if adj_matrix[line][column] != 0:
                dif = randint(-10, 10)
                if (adj_matrix[line][column] + dif) < 0:
                    adj_matrix[line][column] -= dif
                else:
                    adj_matrix[line][column] += dif

#Gera as imagens das árvores de roteamento
def genImage(dotList, vertex, iteration):
    arquivoDot = open(args.outputFile, 'w')
    arquivoDot.write("graph routing {")
    for item in dotList:
        arquivoDot.write(item)
        arquivoDot.write('[label=" ' + str(adj_matrix[int(item[0])][int(item[5])]) + '"]; ')
    if vertex != 'global':
        arquivoDot.write('label="'+'Árvore do roteador '+ str(vertex)+ ' - Iteração ' + str(iteration) + '"; ')
        arquivoDot.write(' }')
        arquivoDot.close()
        os.system('dot -Tpng ' + args.outputFile + ' -o arvore_iter'+ str(iteration)+'_roteador'+str(vertex) + '.png')
    else:
        arquivoDot.write('label="' + 'Árvore Global - Iteração ' + str(iteration) + '"; ')
        arquivoDot.write(' }')
        arquivoDot.close()
        os.system('dot -Tpng ' + args.outputFile + ' -o arvore_global_iter'+ str(iteration) + '.png')

#Cria uma lista com as arestas no formato aceito pelo GraphViz
def createDot(pathList):
    edgesList = []
    dotList = []
    intermediateList = []
    for item in range(len(pathList) - 1):
        if pathList[item] == '-':
            continue
        if pathList[item + 1] != '-':
            edgesList.append(pathList[item])
            edgesList.append(pathList[item + 1])
            edgesList.append('*')

    for item in range(len(edgesList) - 1):
        if (edgesList[item] == '*') or (edgesList[item+1] == '*'):
            continue
        intermediateList.append(str(edgesList[item]) + ' -- ' + str(edgesList[item+1]))

    for item in intermediateList:
        if item not in dotList:
            dotList.append(item)
    return dotList

#Encontra o vértice mais próximo que ainda não está no sptSet
def minDistance(dist, sptSet):
    min = 2147483647

    for v in range(mDim):
        if (sptSet[v] == False and dist[v] <= min):
            min = dist[v]
            min_index = v
    return min_index

#Função para armazenar o caminho mais curto da origem até v
def printPath(parent, v, pathList, src, history):
    if (parent[v] == -1):
        return

    printPath(parent, parent[v], pathList, src, history)
    pathList.append(v)
    history.write(' ' + str(v))

def genGlobal(adj_matrix, iteration):
    globalEdges = []
    for line in range(mDim):
        for column in range(mDim):
            if adj_matrix[line][column] != 0:
                globalEdges.append(str(line)+ ' -- ' + str(column))
    genImage(globalEdges, 'global', iteration)

#Funcão que dá inicio ao armazenaento dos dados de roteamento no arquivo history
def printSolution(dist, parent, src, pathList, history):
    history.write('\n' + '-' * 50)
    history.write('\n' + str(datetime.datetime.now()))
    history.write("\n\nRoteador --- Distancia Minima --- Caminho")
    for v in range(mDim):
        if (v != src):
            pathList.append(src)
        history.write(("\n%d -> %d\t\t\t%d\t\t\t\t\t%d" % (src, v, dist[v], src)))
        printPath(parent, v, pathList, src, history)
        if (v != src):
            pathList.append('-')

def dijkstra(adj_matrix, src, history):
    pathList = []
    dist = np.zeros((mDim), dtype=np.int32)
    sptSet = np.zeros((mDim), dtype=np.int32)
    parent = np.zeros((mDim), dtype=np.int32)

    #Inicializa as distâncias com um valor muito alto e com nenhum vertice no sptSet
    for index in range(mDim):
        parent[src] = -1
        dist[index] =  2147483647
        sptSet[index] = False

    # Distancia da origem a partir de si mesmo será sempre 0
    dist[src] = 0

    #Encontra o menor caminho para todos os vertices
    for vertex in range(mDim):
        u = minDistance(dist, sptSet)

        #Coloca o vertex calculado no sptSet
        sptSet[u] = True

    #Atualiza a distância dos vertices adjacentes ao vertice escolhido
        for v in range(mDim):
            if ((sptSet[v] == False) and (adj_matrix[u][v]) and (dist[u] != 2147483647) and (dist[u] + adj_matrix[u][v] < dist[v])):
                parent[v] = u
                dist[v] = dist[u] + adj_matrix[u][v]

    printSolution(dist, parent, src, pathList, history)
    return pathList

######################### Bloco Principal #########################

initWeights(adj_matrix)
history = open("history.txt", "w")

for iteration in range(args.nIterations):
    genGlobal(adj_matrix, iteration)
    for vertex in range(mDim):
        result = createDot(dijkstra(adj_matrix, vertex, history))
        #Passa a lista das arestas para a funcão que gera as imagens
        genImage(result, vertex, iteration)
    if iteration != args.nIterations - 1:
        time.sleep(args.timeInterval)
        updateWeights(adj_matrix)
history.close()
