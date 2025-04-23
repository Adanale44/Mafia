import asyncio

async def fase_dia(partida):
    canal = partida.canal
    if partida.victima_noche:
        partida.vivo[partida.victima_noche] = False
        await canal.send(f"Amanece. {partida.victima_noche.display_name} ha sido eliminado.")

    vivos = [j for j in partida.jugadores if partida.vivo[j]]
    await canal.send("Debatan quién es el mafioso. Voten con `!votar <nombre>`")
    partida.fase = "dia"
    partida.votos = {}

    await asyncio.sleep(30)
    await contar_votos(partida)

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
    await canal.send(f"{eliminado.display_name} fue eliminado. Era un {partida.roles[eliminado]}")

    await verificar_final(partida)

async def siguiente_noche(partida):
    partida.victima_noche = None
    partida.votos = {}
    await partida.canal.send("Comienza otra noche. Mafioso, elige con `!matar <jugador>`")
    partida.fase = "noche"

async def verificar_final(partida):
    canal = partida.canal
    vivos = [j for j in partida.jugadores if partida.vivo[j]]
    mafias = [j for j in vivos if partida.roles[j] == "Mafioso"]
    ciudadanos = [j for j in vivos if partida.roles[j] != "Mafioso"]

    if not mafias:
        await canal.send("¡Los ciudadanos han ganado!")
        del partida
    elif len(mafias) >= len(ciudadanos):
        await canal.send("¡La mafia ha ganado!")
        del partida
    else:
        await siguiente_noche(partida)