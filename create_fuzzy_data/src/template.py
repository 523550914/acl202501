fuzzy_template = """
You are given a user query and a list of related APIs. Your task is to generate a fuzzier version of the user query by simplifying or replacing technical terms with synonyms, without changing the user's core requirements. You can ollow these steps:
- Analyze the user query: Identify how many tasks the user has and what the specific needs are.
- Compare with the API list: Match the user's tasks with the relevant APIs. Remove any references to specific APIs or redundant technical details.
- Simplify technical terms: Replace highly specialized or technical terms with more common, everyday language. The goal is to make the query sound like something a regular user would say in casual conversation.
- Rephrase the query: Use simpler language or synonyms where appropriate, but ensure the core intent remains unchanged.
- Output the result: Provide the final fuzzier version of the query.

Example1:
Original Query: I'm organizing a gaming tournament for my company's employees. Could you provide the statistics and ratings of highly skilled players in popular games like Dota 2 and World of Tanks? Also, recommend some gaming peripherals and accessories for the event.
Relevant APIs: [tool_name:World of Tanks Stats,api_name:Get Stats],[tool_name:DOTA 2 Steam Web,api_name:Match History],[tool_name:DOTA 2 Steam Web,api_name:Match Details],[tool_name:CheapShark - Game Deals,api_name:List of Deals],[tool_name:CheapShark - Game Deals,api_name:Game Lookup]
Answer:I'm organizing a company gaming tournament and need player stats for top players in popular games. Can you also recommend some good gaming gear for the event?

Example2: 
Original Query: I want to surprise my family with a personalized playlist. Can you recommend some popular tracks from different genres? Additionally, provide me with the detailed information of a playlist that I want to create. Also, fetch the track URL of a specific song that I want to include in the playlist.
Relevant APIs: [tool_name:Shazam,api_name:artists/get-summary],[tool_name:Deezer,api_name:Track],[tool_name:Soundcloud,api_name:/playlist/info]
Answer: I want to make a special playlist for my family. Can you suggest some hit songs from different music styles? Also, give me more info about the playlist I'm putting together. Finally, can you get me the link to a specific track I want to add?

Now, Please make the fuzzier query. 
Original Query: {instruction}
Relevant APIs: {apis}
Answer:

"""



