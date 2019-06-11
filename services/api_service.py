import urllib.request
import json
import os
import requests
from services import menu_service
from classes import userwatcher
from tkinter import *
from PIL import Image, ImageTk

def iconeInv(inv):
    #Checar se icone do invocador já existe
    imgDir = os.listdir("../src/img/")
    imgFile = None
    idIcon = str(getattr(inv, "profileIconId"))
    for f in imgDir:
        if "icon" in f:
            imgFile = f
    if imgFile and idIcon in imgFile:
        img_filename = "../src/img/"+imgFile
        img = Image.open(img_filename)
        return img
    else:
        url ="http://ddragon.leagueoflegends.com/cdn/9.11.1/img/profileicon/" + idIcon+".png"
        getImg = urllib.request.urlopen(url)
        img = Image.open(getImg)
        if imgFile:
            os.remove("../src/img/"+imgFile)
        img.save(("%s/icone"+idIcon+".png") % "../src/img/")
        return img


def checarInvSalvo():
    try:
        with open("../src/dados/inv.json", "r") as r:
            arquivo = json.load(r)
    except:
        return False
    if "invocador" in arquivo.keys():
        invoc = json.loads(arquivo["invocador"])
        cinv = userwatcher.Summoner(invoc)
        return cinv
    else:
        return False

def salvarInv(inv):
    jinv = {"invocador": json.dumps(inv.__dict__)}
    with open("../src/dados/inv.json", "w", encoding="utf-8") as r:
        json.dump(jinv,r)
        r.close()



def statusServidor(key):
    status = requests.get("https://br1.api.riotgames.com/lol/status/v3/shard-data?api_key="+key).json()
    res = ["Game: "+ status["services"][0]["status"], "Client: "+ status["services"][3]["status"]
    ]
    return res



def getQueue(idInvocador, key):
    url = "https://br1.api.riotgames.com/lol/league/v4/entries/by-summoner/"+idInvocador+"?api_key="+key
    res = requests.get(url).json()
    return res

def getFullLeague(leagueId, key):
    url = "https://br1.api.riotgames.com/lol/league/v4/leagues/"+leagueId+"?api_key="+key
    res = requests.get(url).json()
    return res


def getLastMatches(invId, key):
    url = "https://br1.api.riotgames.com/lol/match/v4/matchlists/by-account/"+indId+"?api_key="+key
    res = requests.get(url).json()
    return res["matches"]


#Pegar partidas jogadas por um invocador com determinados campeoes
def filterMatchesChampions(key, matches, idChampions, inv):
    #Vitorias e derrotas com o campeão
    winsLosesByChampion = {idChampions[0]: [0,0], idChampions[1]: [0,0], idChampions[2]: [0,0]}
    for mat in matches:
        #Baixar resultados de cada partida separadamente
        urlMat = "https://br1.api.riotgames.com/lol/match/v4/matches/"+mat["gameId"]+"?api_key="+key 
        resMat = requests.get(urlMat).json()
        idPlayerInMatch = None
        #Encontrar o ID do invocador dentro da partida
        for player in resMat["participantIdentities"]:
            if player["player"]["summonerName"] == inv.name:
                idPlayerInMatch = int(player["participantId"])
                break
        #Pegar informações individuais do invocador na partida
        playerStatusInMatch = resMat["participants"][idPlayerInMatch]
        idChampionInMatch = int(playerStatusInMatch["championId"])
        #Verificar se o campeão escolhido na partida é um dos mains do invocador
        if idChampionInMatch in idChampions:
            #Verificar se o invocador ganhou ou perdeu o jogo
            win = (resMat["teams"][0]["win"] if idPlayerInMatch <= 5 else resMat["teams"][1]["win"]) == "Win"
            if win:
                winsLosesByChampion[idChampionInMatch][0] += 1
            else:
                winsLosesByChampion[idChampionInMatch][1] += 1

    print(winsLosesByChampion)
