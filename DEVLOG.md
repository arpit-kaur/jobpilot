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