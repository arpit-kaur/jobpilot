# Dev log

Notes I wrote while building JobPilot. What I built each day, what broke and what I want to fix.

## Oct 31

Started with plain Python and no AI. I wanted the basic functions working first before letting a model decide anything. So I wrote three of them. One reads a saved job posting, one compares it with my skills and one saves a job to a CSV tracker.

The skill check had a problem right away. Checking if a word is in the text means Java matches inside JavaScript and Git matches inside digital. I changed it to match whole words only. With my two sample postings I got 78 percent for the AI developer job, missing Docker and CI/CD, and 73 percent for the .NET job, missing React, TypeScript and Docker.

It is still just keyword matching. The .NET posting says Azure DevOps and the checker counts that as Azure. Fine for now but I should remember it.

If you ask for a posting that does not exist, the function returns the list of files that do exist instead of crashing. I did this because later the model will read that message and can try again with the right name.

Then I connected Llama 3.1 through Ollama. I give it the three functions and a request and it picks which one to call and what to pass in. It does not run anything itself. It sends back a request and my code runs the function. When I asked it to save the .NET developer job at Riverbend Software it picked the right function, pulled out the company and the role, and even filled in the default status by itself.

The greeting was weird. I typed hi how are you and it did not call any tool, which is right, but the reply was a confusing paragraph about function calls with an empty JSON at the end. I think having tools attached with no instructions confused it. A system prompt should fix that.

Next step is a real agent loop where the result goes back to the model so it can decide what to do next.

## Nov 1

Today I built the agent loop myself. No framework.

The idea is simple. The chat is just a list in Python. My question goes in. Llama replies. If it asks for a tool, my code runs the tool and adds the result to the list. Then the whole list goes back to Llama so it can decide what to do next. When it stops asking for tools, that is the final answer.

I also gave Llama some basic instructions at the start. Yesterday it gave a strange reply when I just said hi. Now it simply says it is doing well.

Then I asked it to read the riverbend posting without giving the full file name. Llama asked for riverbend.txt. That file does not exist, so my tool sent back the list of real file names.

The first time, Llama knew the right file name but it typed the request as normal text instead of actually using the tool. My code thought it was done and stopped. I added a check for this. If Llama types the request as text, my code tells it to use the tool and gives it another try.

The next time, it gave the job title without opening the file at all. It just read the title from the file name. I could tell because it wrote DotNet Developer like the file name, but the posting says .NET Developer. I told Llama in the instructions to never guess. It still guessed.

So I changed the tool instead. If the file name is not exact but only one posting has that word in its name, the tool just opens that posting. Now Llama gets the real posting right away and has nothing to guess from. The answer now matches the posting.

I also set the temperature to 0. Before that, every run gave a different answer, so it was hard to tell if my fix really worked.

Biggest lesson today. Always check where an answer came from. An answer can look right and still be a guess.

## Nov 2

Today I asked the agent to do three things in one request. Read the prairie posting, check my skills against it and save it to my tracker. It took a lot longer than I planned.

Llama asked for all three tools at the same time, before it had even read the posting. It gave the skill check nonsense and my code crashed. I changed the code so a wrong input goes back to the model as a message instead of crashing everything.

Then I made the code run only one tool per round. That way the model has to wait for each result before it decides the next step.

After that Llama only read the posting and then said it had compared my skills and saved the job. It did neither. There was no new row in my tracker. This one worried me the most because the answer sounded finished. Now the code prints the list of tools that really ran next to every answer. If the answer says saved but the list has no save tool, I see it right away.

Llama also kept asking me for my skills. The tool reads them from a file by itself, but the tool description never said that. I added one line saying my skills are already saved.

It still did not do all three steps, so I tried Qwen 2.5 on the same requests. Qwen read the posting, passed the full text to the skill check, got 78 percent and saved the job with the real company name from the posting. Same task and same prompt but a different model. I switched to Qwen.

I also learned how easily prompts break. I changed one line to fix one request and it broke another one. I went back to the last version that worked.

What works now. The greeting, finding the riverbend posting and the full read, compare and save task. What does not work yet. If I type the skills in my question, the model looks for a file instead of checking them. The final answer also only mentions the save and not the match. I will add tests before trying to fix these.

I also ran my skill check on three real jobs I am interested in. Price came out at 75 percent, Affirm at 50 percent and Wawanesa at 29 percent. AWS was missing in two of the three. It also showed me where keyword matching falls short. Price asks for Azure or AWS and I have Azure, but the tool still counts AWS as missing. It also missed RESTful because it only looks for the exact word REST.

## Nov 3

Today I rebuilt the same agent with LangGraph and kept my hand written version next to it. Same model, same prompt and same tools, so I could compare them fairly.

Every part of LangGraph matched something I already wrote. The state is my message list. The tool node is my code that runs the tool. The arrow from the tools back to the model is my loop. The recursion limit is my max steps. Last week this all felt like magic. Now it just feels like a shorter way to write what I already built.

The greeting, the riverbend posting and the skills question behaved the same in both versions. The three step request did not. In the LangGraph version the model read the posting and then came back with a completely empty answer.

Instead of changing the prompt again I printed the whole reply. It had no text and no tool call, but it said the model had written 120 tokens. That is about the size of the posting. So the model most likely tried to pass the whole posting to the skill check and that request got lost somewhere between Ollama and LangChain.

I added a small retry. If the reply comes back completely empty, the code asks the model to continue. That got it moving again. It ran the skill check and gave me the 78 percent match in the answer, which my first version never did. But it never ran the save tool and still said it saved the job. My tools actually used list showed it right away.

So the same model acts differently depending on how the request is sent to it. For this project my hand written loop is the more reliable one. Next I want the code to catch false claims like this by itself instead of me reading the output.

## Nov 4

Today was about making the agent safer without relying on the model to behave.

First I fixed the problem from yesterday where the model said it saved a job when it did not. I wrote a small check in plain Python. After the model answers, the code looks for the word saved. If the answer says saved but the save tool never ran, it adds a warning saying nothing was saved. It ignores answers that say not saved, because those are honest.

To make that check reliable I had to fix how I count tools. Before, a tool was added to the list as soon as the model asked for it. Now it only gets added after it actually runs.

Then I added an approval step. Reading a posting and comparing skills do not change anything, so they run on their own. Saving writes to my tracker, so now the agent stops and asks me first. If I say no, the tool does not run and the model is told it was not approved.

I also wrote my first tests with pytest. Six tests check the tools, like the whole word skill match, finding the riverbend posting from a close name and the 78 percent match on the prairie posting. One test saves a fake job, so I used a temporary file to keep my real tracker clean. Three more tests check the warning for false save claims. None of the tests use the model, so they run in under a second and give the same result every time.

Last I set up GitHub Actions. Every time I push, GitHub runs all 9 tests on a fresh Linux machine. The first run passed in about 10 seconds.

## Nov 5

Today was about getting the project ready for other people to see.

I wrote the README and took a screenshot of a full run, from reading the posting to approving the save. The first screenshot cut off the missing skills, because the code only printed the first 100 characters of each result. I raised it to 130 so the full match line shows.

Before making the repo public I checked that my real job postings and my tracker were never committed, not even in old commits. They are in the gitignore and the history was clean.

The repo is public now, with a description, topics and a test badge that updates on every push.