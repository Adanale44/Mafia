async def verificar_final(partida):
    canal = partida.canal
    vivos = [j for j in partida.jugadores if partida.vivo[j]]
    mafias = [j for j in vivos if partida.roles[j] == "Mafioso"]
    ciudadanos = [j for j in vivos if partida.roles[j] != "Mafioso"]

    if not mafias:
        await canal.send("¡Los ciudadanos han ganado!")
        return await terminar_partida(partida)
    elif len(mafias) >= len(ciudadanos):
        await canal.send("¡La mafia ha ganado!")
        return await terminar_partida(partida)
    else:
        await iniciar_noche(partida)

async def iniciar_noche(partida):
    from comandos.fase_noche import iniciar_noche as iniciar
    await iniciar(partida)

async def terminar_partida(partida):
    del partida.canal.bot.partidas[partida.canal.id]
