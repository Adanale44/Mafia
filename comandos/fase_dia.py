import discord
from discord.ext import commands
import asyncio
from comandos.verificar_final import verificar_final, iniciar_noche

def registrar_comandos_dia(bot, partidas):
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

async def iniciar_dia(partida):
    canal = partida.canal
    if partida.victima_noche:
        partida.vivo[partida.victima_noche] = False
        await canal.send(f"Amanece... y {partida.victima_noche.display_name} ha sido eliminado.")
    else:
        await canal.send("Amanece... nadie murió.")

    partida.fase = "dia"
    partida.votos = {}
    vivos = [j for j in partida.jugadores if partida.vivo[j]]
    await canal.send("Debatan y voten con `!votar <nombre>`.")
    await asyncio.sleep(30)
    await contar_votos(partida)

async def contar_votos(partida):
    canal = partida.canal
    conteo = {}
    for votante, objetivo in partida.votos.items():
        conteo[objetivo] = conteo.get(objetivo, 0) + 1

    if not conteo:
        await canal.send("Nadie fue votado. Nadie será eliminado.")
        await iniciar_noche(partida)
        return

    eliminado = max(conteo, key=conteo.get)
    partida.vivo[eliminado] = False
    await canal.send(f"{eliminado.display_name} fue eliminado. Era {partida.roles[eliminado]}")
    await verificar_final(partida)
