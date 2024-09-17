import ollama
import discord,os
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
intent=discord.Intents.default()
intent.message_content=True
bot=commands.Bot(command_prefix='/',intents=intent)
@bot.event
async def on_ready():
    print(f"Bot is ready as {bot.user.name}")

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send("Hello, I am a bot!")

@bot.command(name='ask')
async def ask(ctx, *, question: str):
    # Get a response from the ollama API
    response = ollama.chat(model='llama3.1', messages=[
         {
            'role': 'system',
            'content': 'You are a helpful assistant who provides answers to questions conscisely in less than 2000 words',
        },
        {
            'role': 'user',
            'content': question,
        },
    ])
    
    # Extract the response message from ollama and send it back to the user
    reply = response['message']['content']
    print(response['message']['content'])
    await ctx.send(reply)

@bot.command(name='summarise')
async def summarise(ctx):
    # Get a response from the ollama API
    #print(question)
    print('-------------------')
    summary=[qn.content async for qn in ctx.channel.history(limit=10)]
    summarise_prompt=f"""
    Summarise the following messages delimited by 3 backticks:
    ```
    {summary}
    ```
    """
    response = ollama.chat(model='llama3.1', messages=[
         {
            'role': 'system',
            'content': 'You are a helpful assistant who provides answers to questions conscisely in less than 2000 words',
        },
        {
            'role': 'user',
            'content': summarise_prompt,
        },
    ])
    
    # Extract the response message from ollama and send it back to the user
    reply = response['message']['content']
    print(response['message']['content'])
    await ctx.send(reply)
    '''
    for i in range(0, len(reply), 2000):
        await ctx.send(reply[i:i+2000])
    '''

bot.run(os.getenv('DISCORD_ID'))

'''   
response = ollama.chat(model='llama3.1', messages=[
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
])
print(response['message']['content'])
'''