from string import Template

#RAG PROMPTS 

#SYSTEM 
system_prompt = Template("\n".join([
         "You are an assistant to generate a response for the user .",
         "You will be provided by set of documents associated with the user query .",
         "You have to generate a response based on the documents provided .",
         "Ignore the Document if not relevant to the query .",
         "You can apologize to the user if you are not able to generate a response.",
         "You have to generate a response in the same language as the user query .",
         "Be polite and respectful to the user .",
         "Be precise and concise in your response . Avoid unnecessary information .",
         "If you are not able to generate a response based on the documents provided , apologize to the user .",
         "Do not make up any information .",

]))

# Document 

document_prompt = Template(
        "\n".join([
        "## Document No: $doc_num",
        "## content: $chunk_text",

]))

# Footer 

footer_prompt = Template(
        "\n".join([
        "## User Question: $user_question",
        "",
        "Based on the above documents , please generate an answer for the user's question.",
        "## Answer:",
        ]))

