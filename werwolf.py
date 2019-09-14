#!/usr/bin/python3
from flask import Flask,render_template,request,url_for,redirect
from pprint import pprint
from uuid import uuid4
from random import shuffle
app = Flask(__name__)

games = {}

EXTRA_ROLES = [ "Seherin", "Hexe", "Amor", "Jäger" ]
WEREWOLVE_PERCENTAGE = 20
MIN_PLAYERS = 5

class NotEnoughPlayersError(Exception):
    pass

@app.route("/")
def new_game():
    return render_template("new_game.html", roles=EXTRA_ROLES)

@app.route("/", methods=["post"])
def create_game():
    global games
    pnames = [ x for x in request.form.getlist("pname") if x != "" ]
    used_roles = [ x for x in request.form.getlist("roles") if x != "" ]
    gameid = str(uuid4())

    num_players = len(pnames)
    if not num_players >= MIN_PLAYERS:
        raise NotEnoughPlayersError

    num_werewolves = round(num_players * (WEREWOLVE_PERCENTAGE / 100))
    card_stack = []
    card_stack.extend([ "Werwolf" ] * num_werewolves)
    card_stack.extend(used_roles)
    while len(card_stack) < num_players:
        card_stack.append("Dorfbewohner")

    pprint(card_stack)
    assert len(card_stack) == num_players
    shuffle(card_stack)
    pprint(card_stack)

    mapping = {}
    for i, player in enumerate(pnames):
        mapping[player] = card_stack[i]

    games[gameid] = {}
    games[gameid]["mapping"] = mapping
    games[gameid]["num_werewolves"] = num_werewolves
    games[gameid]["used_roles"] = used_roles

    return redirect(url_for("player_select", gameid=gameid),303)

@app.route("/game/<uuid:gameid>/")
def player_select(gameid):
    return render_template("player_select.html", players=games[str(gameid)]["mapping"].keys(), gameurl=url_for("player_select", gameid=gameid))

@app.route("/game/<uuid:gameid>/show/<player>")
def name_show(gameid, player):
    return render_template("name_show.html", current_player=player,
                                             own_role=games[str(gameid)]["mapping"][player],
                                             used_roles=games[str(gameid)]["used_roles"],
                                             num_players=len(games[str(gameid)]["mapping"]),
                                             num_werewolves=games[str(gameid)]["num_werewolves"])

#@app.errorhandler(KeyError)
#def not_found(error):
#    return "<h1>Not Found</h1>Object not found <br/> <a href={}>home</a>".format(url_for("create_game")), 404

@app.errorhandler(NotEnoughPlayersError)
def not_found(error):
    return "<h1>Not Enough Players</h1>You need at least {} players to play Werewolves<br/> <a href={}>home</a>".format(MIN_PLAYERS, url_for("create_game")), 404