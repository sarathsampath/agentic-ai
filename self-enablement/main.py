from langchain_aws import ChatBedrock


custom_llm = ChatBedrock(
    credentials_profile_name="xyz",
    provider="anthropic",
    model_id="arn:aws:bedrock:us-east-1:xyz:inference-profile/us.anthropic.claude-3-5-haiku-20241022-v1:0",
    model_kwargs={"temperature": 1},
    region_name="us-east-1",
)

result = custom_llm.invoke(input="What is the recipe of mayonnaise?")
print(result.content)