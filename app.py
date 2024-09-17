import ollama
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import tiktoken

load_dotenv()
intent = discord.Intents.default()
intent.message_content = True
bot = commands.Bot(command_prefix='/', intents=intent)

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
            'content': 'You are a helpful assistant who provides answers to questions concisely in less than 2000 words.',
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

@bot.command(name='yt_transcript')
async def yt_transcript(ctx, url):
    await ctx.send("Summarizing the YouTube video...")
    
    try:
        # Extract the video ID from the URL
        video_id = url.split('v=')[1]
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine the transcript texts into one string
        full_transcript = " ".join([item['text'] for item in transcript_list])
        
        # Tokenize the transcript using tiktoken
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        tokens = encoding.encode(full_transcript)
        num_tokens = len(tokens)
        
        print(f"Total tokens: {num_tokens}")
        
        chunk_size = 4000
        if num_tokens > chunk_size:
            num_chunks = (num_tokens + chunk_size - 1) // chunk_size
            chunks = [full_transcript[i * chunk_size:(i + 1) * chunk_size] for i in range(num_chunks)]
        
            async def process_chunk(chunk, chunk_num):
                await ctx.send(f"Extracting summary of chunk {chunk_num} of {num_chunks}...")
                # Get a response from the ollama API
                response = ollama.chat(model='llama3.1', messages=[
                    {
                        'role': 'system',
                        'content': 'You are a helpful assistant who summarizes YouTube video transcript in bullet points concisely in no more than 1000 words.',
                    },
                    {
                        'role': 'user',
                        'content': f'''
                        Please provide a summary fo the following chunk of youtube video transcript:
                        1.Strat with a high level title of this chunk
                        2.Provide 6-8 bullet points summarising the key points in this chunk
                        3.Start with title of chunk and then provide summary in bullet points instead
                        4.No need to use concluding remarks at the end
                        5.Return the response in markdown format

                        Chunk:
                        
          
                        {chunk}
                        ''',
                    },
                ])
                return response['message']['content']
        
            for i, chunk in enumerate(chunks, start=1):
                summary = await process_chunk(chunk, i)
                await ctx.send(summary)
    
        else:
            # If the transcript is small enough, summarize it directly
            response = ollama.chat(model='llama3.1', messages=[
                 {
                    'role': 'system',
                    'content': 'You are a helpful assistant who provides a concise summary of the provided video transcript in bullet points.',
                },
                {
                    'role': 'user',
                    'content': full_transcript,
                },
            ])
            
            # Extract the response message from ollama and send it back to the user
            reply = response['message']['content']
            print(reply)
            await ctx.send(reply)

    except Exception as e:
        print(e)
        await ctx.send("An error occurred while processing the YouTube transcript.")


@bot.command(name='extract_ideas')
async def extract_ideas(ctx, url):
    await ctx.send("Extracting from the YouTube video...")
    
    try:
        # Extract the video ID from the URL
        video_id = url.split('v=')[1]
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine the transcript texts into one string
        full_transcript = " ".join([item['text'] for item in transcript_list])
        
        # Tokenize the transcript using tiktoken
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        tokens = encoding.encode(full_transcript)
        num_tokens = len(tokens)
        
        print(f"Total tokens: {num_tokens}")
        
        chunk_size = 4000
          # Get a response from the ollama API
        response = ollama.chat(model='llama3.1', messages=[
        {
          'role': 'system',
          'content': '''You are an expert youtube content creator who is
           an expert at analysing ideos and extracting key ideas ''',
        },
        {
          'role': 'user',
          'content': f'''
           Extract 3 key ideas based on topic,ideas,concepts, or thoughts discussed
           in the following video transcript which are similar to    provided video          

           Each video idea should have:
           1.Title of video
           2.2-line description of what that video would look like  
           Video transcript
           {full_transcript}
          ''',
          },
        ])
           
        
           
            # Extract the response message from ollama and send it back to the user
        reply = response['message']['content']
        print(reply)
        await ctx.send(reply)

    except Exception as e:
        print(e)
        await ctx.send("An error occurred while processing the YouTube transcript.")

@bot.command(name='summarise')
async def summarise(ctx):
    # Collect last 10 messages from the channel
    summary = [qn.content async for qn in ctx.channel.history(limit=10)]
    summarise_prompt = f"""
    Summarize the following messages delimited by 3 backticks:
    ```
    {summary}
    ```
    """
    response = ollama.chat(model='llama3.1', messages=[
         {
            'role': 'system',
            'content': 'You are a helpful assistant who provides answers to questions concisely in less than 2000 words.',
        },
        {
            'role': 'user',
            'content': summarise_prompt,
        },
    ])
    
    # Extract the response message from ollama and send it back to the user
    reply = response['message']['content']
    print(reply)
    await ctx.send(reply)

bot.run(os.getenv('DISCORD_ID'))
