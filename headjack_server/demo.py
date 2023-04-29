import asyncio


async def main():
    tools = [KnowledgeSearchTool()]
    agent = StandardAgent(
        model_identifier="chatgpt",
        tools=tools,
        decoder="argmax(openai_chunksize=4)",
    )

    return await agent.run(User("how much were q4 earnings"), 3, {User, Answer}, 4, [], [])


if __name__ == "__main__":
    asyncio.run(main())
