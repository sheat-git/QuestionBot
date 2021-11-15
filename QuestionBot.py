import discord
import aiohttp
import os
import io

TOKEN = os.environ['QUESTIONBOT_TOKEN']
Q_CHANNEL_ID = os.environ['QUESTION_CHANNEL_ID']
Q_CHANNEL = None
template = f'__以下の内容を <#{Q_CHANNEL_ID}> に送信します。\nよろしければ :o: を押してください。__'
client = discord.Client()


@client.event
async def on_ready():
    print(f'logged in as {client.user}')
    global Q_CHANNEL
    Q_CHANNEL = client.get_channel(int(Q_CHANNEL_ID))


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if str(message.channel.type) != 'private':
        return
    files = []
    for f in message.attachments:
        async with aiohttp.ClientSession() as session:
            async with session.get(f.url) as resp:
                if resp.status != 200:
                    return message.channel.send(f'[{f.filename}]({f.url}) の取得に失敗しました。')
                files.append(discord.File(io.BytesIO(await resp.read()), f.filename))
    if not files:
        files = None
    msg = await message.channel.send(f'{template}\n{message.content}', files=files)
    await msg.add_reaction('⭕')


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == client.user.id:
        return
    channel = client.get_channel(payload.channel_id)
    if str(channel.type) != 'private':
        return
    message = await channel.fetch_message(payload.message_id)
    Oflag = False
    for reaction in message.reactions:
        if reaction.emoji == '⭕':
            Oflag = True
            break
    if not Oflag:
        return
    files = []
    for f in message.attachments:
        async with aiohttp.ClientSession() as session:
            async with session.get(f.url) as resp:
                if resp.status != 200:
                    return channel.send(f'[{f.filename}]({f.url}) の取得に失敗しました。')
                files.append(discord.File(io.BytesIO(await resp.read()), f.filename))
    if not files:
        files = None
    await Q_CHANNEL.send(message.content.replace(template+'\n', ''), files=files)
    await channel.send(f'<#{Q_CHANNEL_ID}> に送信完了しました。')


client.run(TOKEN)
