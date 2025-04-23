import discord
from discord.ext import commands
import asyncio
from comandos.fase_dia import iniciar_dia

def registrar_comandos_noche(bot, partidas):
    @bot.command()
    async def matar(ctx, objetivo: discord.Member):
        canal = ctx.channel
        if canal.id not in partidas:
            return

        partida = partidas[canal.id]
        if partida.fase != "noche":
            return

        if partida.roles.get(ctx.author) != "Mafioso":
            return

        if not partida.vivo.get(objetivo, False):
            await ctx.send("Ese jugador ya está muerto.")
            return

        partida.victima_noche = objetivo
        await ctx.send("Elección recibida. El juego continuará al amanecer.")
        await asyncio.sleep(2)
        await iniciar_dia(partida)

async def iniciar_noche(partida):
    canal = partida.canal
    partida.victima_noche = None
    partida.votos = {}
    partida.fase = "noche"
    await canal.send("Empieza la noche. Mafioso, elige a quién matar con `!matar <nombre>`.")
    await asyncio.sleep(120)
    if partida.victima_noche is None:
        await canal.send("El mafioso no hizo su jugada. Nadie murió.")
        await iniciar_dia(partida)
