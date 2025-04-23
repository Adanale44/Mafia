import discord
from discord.ext import commands
import random
from comandos.fase_noche import iniciar_noche

roles_disponibles = ["Mafioso", "Doctor", "Detective"]

class Partida:
    def __init__(self, canal):
        self.canal = canal
        self.jugadores = []
        self.roles = {}
        self.vivo = {}
        self.fase = "espera"
        self.victima_noche = None
        self.votos = {}

def registrar_comandos_partida(bot, partidas):
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
                await ctx.send("Se necesitan al menos 3 jugadores.")
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

    await iniciar_noche(partida)
