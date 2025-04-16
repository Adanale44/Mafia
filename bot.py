import discord
from discord.ext import commands
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

partidas = {}
roles_disponibles = ["Mafioso", "Doctor", "Detective"]

class Partida:
    def __init__(self, canal):
        self.canal = canal
        self.jugadores = []
        self.roles = {}
        self.vivo = {}
        self.fase = "espera"  # espera, noche, dia
        self.victima_noche = None
        self.votos = {}

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.command()
async def mafia(ctx, accion: str):
    canal = ctx.channel

    if accion == "crear":
        if canal.id in partidas:
            await ctx.send("Ya hay una partida en este canal.")
            return

        partidas[canal.id] = Partida(canal)
        await ctx.send("Partida creada. Usa `!mafia unirme` para entrar. Usa `!mafia iniciar` cuando estén listos.")

    elif accion == "unirme":
        if canal.id not in partidas:
            await ctx.send("No hay partida activa.")
            return

        partida = partidas[canal.id]
        if ctx.author in partida.jugadores:
            await ctx.send("Ya estás en la partida.")
            return

        partida.jugadores.append(ctx.author)
        partida.vivo[ctx.author] = True

        await ctx.send(f"{ctx.author.display_name} se unió. Jugadores actuales: {len(partida.jugadores)}")

    elif accion == "iniciar":
        if canal.id not in partidas:
            await ctx.send("No hay partida activa.")
            return
        partida = partidas[canal.id]
        if len(partida.jugadores) < 3:
            await ctx.send("Se necesitan al menos 3 jugadores para comenzar.")
            return
        await iniciar_partida(ctx, partida)

async def iniciar_partida(ctx, partida):
    jugadores = partida.jugadores.copy()
    random.shuffle(jugadores)
    roles = ["Mafioso"] + roles_disponibles[:min(2, len(jugadores)-1)]
    roles += ["Ciudadano"] * (len(jugadores) - len(roles))
    random.shuffle(roles)

    for jugador, rol in zip(jugadores, roles):
        partida.roles[jugador] = rol
        try:
            await jugador.send(f"Tu rol es: {rol}")
        except:
            await ctx.send(f"No pude enviar mensaje a {jugador.display_name}.")

    await ctx.send("Empieza la noche. Mafioso, elige a quién matar con `!matar <nombre>`. Tienes 2 minutos.")
    partida.fase = "noche"

    try:
        await asyncio.wait_for(esperar_matar(partida), timeout=120)
    except asyncio.TimeoutError:
        await partida.canal.send("Se acabó el tiempo. Nadie fue eliminado esta noche.")
        await fase_dia(partida)

async def esperar_matar(partida):
    while partida.fase == "noche" and not partida.victima_noche:
        await asyncio.sleep(1)

@bot.command()
async def matar(ctx, objetivo: discord.Member):
    canal = ctx.channel
    if canal.id not in partidas:
        return

    partida = partidas[canal.id]

    if partida.fase != "noche":
        return

    autor = ctx.author
    if partida.roles.get(autor) != "Mafioso":
        return

    if not partida.vivo.get(objetivo, False):
        await ctx.send("Ese jugador ya está muerto.")
        return

    partida.victima_noche = objetivo
    await ctx.send("Elección recibida. El juego continuará al amanecer.")
    await fase_dia(partida)

async def fase_dia(partida):
    canal = partida.canal
    if partida.victima_noche:
        partida.vivo[partida.victima_noche] = False
        await canal.send(f"Amanece... y se descubre que {partida.victima_noche.display_name} ha sido eliminado.")

    vivos = [j for j in partida.jugadores if partida.vivo[j]]
    await canal.send("Discutan quién podría ser el mafioso. Voten con `!votar <nombre>`.")
    partida.fase = "dia"
    partida.votos = {}

    await asyncio.sleep(20)
    await contar_votos(partida)

@bot.command()
async def votar(ctx, objetivo: discord.Member):
    canal = ctx.channel
    if canal.id not in partidas:
        return

    partida = partidas[canal.id]
    if partida.fase != "dia":
        return

    if not partida.vivo.get(ctx.author, False):
        return

    if not partida.vivo.get(objetivo, False):
        return

    partida.votos[ctx.author] = objetivo
    await ctx.send(f"Voto registrado de {ctx.author.display_name} contra {objetivo.display_name}")

async def contar_votos(partida):
    canal = partida.canal
    conteo = {}
    for votante, objetivo in partida.votos.items():
        conteo[objetivo] = conteo.get(objetivo, 0) + 1

    if not conteo:
        await canal.send("Nadie fue votado. Nadie será eliminado.")
        await siguiente_noche(partida)
        return

    eliminado = max(conteo, key=conteo.get)
    partida.vivo[eliminado] = False
    await canal.send(f"{eliminado.display_name} ha sido eliminado por votación. Era un {partida.roles[eliminado]}")

    await verificar_final(partida)

async def verificar_final(partida):
    canal = partida.canal
    vivos = [j for j in partida.jugadores if partida.vivo[j]]
    mafias = [j for j in vivos if partida.roles[j] == "Mafioso"]
    ciudadanos = [j for j in vivos if partida.roles[j] != "Mafioso"]

    if not mafias:
        await canal.send("Los ciudadanos han ganado!")
        del partidas[canal.id]
    elif len(mafias) >= len(ciudadanos):
        await canal.send("La mafia ha ganado!")
        del partidas[canal.id]
    else:
        await siguiente_noche(partida)

async def siguiente_noche(partida):
    partida.victima_noche = None
    partida.votos = {}
    await partida.canal.send("Comienza otra noche. Mafioso, elige con `!matar <jugador>`. Tienes 2 minutos.")
    partida.fase = "noche"

    try:
        await asyncio.wait_for(esperar_matar(partida), timeout=120)
    except asyncio.TimeoutError:
        await partida.canal.send("Se acabó el tiempo. Nadie fue eliminado esta noche.")
        await fase_dia(partida)

bot.run("MTM2MTUxODExODMxNjQwODgzMg.GjSIvC.l8bnbyp53USaI82EoMedwVoIBGHWoC8Ka-KghQ")
