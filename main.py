from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def main():
    response = client.responses.create(
        model="gpt-4.1", input="Write a one-sentence bedtime story about a unicorn."
    )

    print(response.output_text)


if __name__ == "__main__":
    main()
